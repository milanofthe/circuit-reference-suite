"""Run circuits on simulators: every analysis of a circuit on every adapter that can read
its body, under a time and memory limit, signals and timings kept.

    out/results.jsonl                       one line per circuit, simulator and analysis
    out/<simulator>/<circuit>/<k>.npz       the signals of analysis k
    out/<simulator>/<circuit>/<k>.log       what the simulator printed

One line per finished circuit and simulator goes to the log as it happens.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import re
import resource
import shutil
import signal
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from . import raw
from .adapters import ADAPTERS, Adapter
from .circuit import Circuit, iter_circuits
from .stage import Compiler, StageError, stage, tail
from .translate import Untranslatable, translate


def _limits(memory: int):
    def apply():
        try:
            resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        except (ValueError, OSError):                   # macOS: no address-space limit
            pass
    return apply


def run_circuit(c: Circuit, ad: Adapter, work: Path, out: Path, compiler: Compiler,
                timeout: float, memory_gb: float) -> list[dict]:
    base = {"circuit": c.name, "simulator": ad.name, "version": ad.version()}
    nl = next((c.variants[d] for d in ad.dialects if d in c.variants), c.source)
    if nl.dialect not in ad.dialects:
        base["translated"] = nl.dialect
    dest = work / hashlib.sha1(f"{c.name}/{ad.name}".encode()).hexdigest()[:12]
    shutil.rmtree(dest, ignore_errors=True)
    keep = out / ad.name / c.name
    keep.mkdir(parents=True, exist_ok=True)
    records = []
    try:
        try:
            netlist, osdi = stage(c.case, nl, dest, ad.osdi, compiler)
            ad.preload(netlist.parent, osdi)
        except (StageError, NotImplementedError) as e:
            return [base | {"status": "stage-failed", "message": str(e)}]
        if "translated" in base:
            try:
                translate(c.case, nl, dest, ad.dialects[0])
            except Untranslatable as e:
                return [base | {"status": "untranslated", "message": str(e)}]
        text = netlist.read_bytes().decode("latin-1")
        for k, a in enumerate(c.analyses):
            rec = base | {"analysis": k, "type": a["type"]}
            deck = netlist.with_name(f"{netlist.stem}.circref{k}.cir")
            rawfile = deck.with_suffix(".raw")
            deck.write_bytes(ad.deck(c, text, a).encode("latin-1"))
            t0 = time.monotonic()
            proc = subprocess.Popen(ad.argv(deck.name, rawfile.name), cwd=netlist.parent,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, start_new_session=True,
                                    preexec_fn=_limits(int(memory_gb * 2**30)))
            try:
                output, _ = proc.communicate(timeout=timeout)
                timed_out = False
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                output, _ = proc.communicate()
                timed_out = True
            rec["wall_s"] = round(time.monotonic() - t0, 4)
            log = output.decode("latin-1")
            (keep / f"{k}.log").write_text(log)
            if ad.timing and (m := re.search(ad.timing, log)):
                rec["sim_s"] = float(m.group(1))
            rc = proc.returncode
            if timed_out:
                rec |= {"status": "timeout"}
            elif rc < 0:
                rec |= {"status": "killed", "exit": rc}
            elif rc or not rawfile.exists():
                rec |= {"status": "failed", "exit": rc, "message": tail(log)}
            else:
                try:
                    plots = raw.read(rawfile.read_bytes())
                except Exception as e:
                    rec |= {"status": "failed", "message": f"rawfile: {type(e).__name__}: {e}"}
                else:
                    signals = {name: v for p in plots[-1:] for name, v in p.signals.items()}
                    np.savez_compressed(keep / f"{k}.npz", **signals)
                    rec |= {"status": "ok", "points": len(next(iter(signals.values()), [])),
                            "signals": len(signals)}
            records.append(rec)
        return records
    finally:
        shutil.rmtree(dest, ignore_errors=True)


def select(patterns: list[str]) -> list[Circuit]:
    return [c for c in iter_circuits()
            if not patterns or any(fnmatch.fnmatch(c.name, p) for p in patterns)]


def run(circuits: list[Circuit], adapters: list[Adapter], out: Path, workers: int,
        timeout: float, memory_gb: float, shard: tuple[int, int] = (0, 1)) -> int:
    jobs = [(c, a) for c in circuits for a in adapters]
    jobs = jobs[shard[0]::shard[1]]
    out.mkdir(parents=True, exist_ok=True)
    work = Path(os.environ.get("CIRCREF_WORK", "/scratch/circref"))
    compiler = Compiler(out / "osdi")
    counts: dict[str, int] = {}
    t0 = time.monotonic()
    with open(out / "results.jsonl", "a") as results, ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(run_circuit, c, a, work, out, compiler, timeout, memory_gb): (c, a)
                   for c, a in jobs}
        for done, f in enumerate(as_completed(futures), 1):
            c, a = futures[f]
            try:
                recs = f.result()
            except Exception as e:                  # a bug in circref, not in the circuit
                recs = [{"circuit": c.name, "simulator": a.name, "status": "error",
                         "message": f"{type(e).__name__}: {e}"}]
            for r in recs:
                results.write(json.dumps(r) + "\n")
                counts[r["status"]] = counts.get(r["status"], 0) + 1
            results.flush()
            status = ",".join(r["status"] for r in recs)
            wall = sum(r.get("wall_s", 0) for r in recs)
            msg = next((r["message"] for r in recs if "message" in r), "").replace("\n", " ")[:100]
            print(f"[{done}/{len(jobs)} {time.monotonic() - t0:6.0f}s] {a.name:8s} {status:14s} "
                  f"{wall:8.2f}s {c.name}  {msg}", flush=True)
    print(" ".join(f"{k}={v}" for k, v in sorted(counts.items())), flush=True)
    return 0
