"""Run circuits on simulators: every analysis of a circuit on every adapter that can read
its body, at every precision level of bench.toml, under a time and memory limit, signals
and timings kept.

    out/results.jsonl                               one line per circuit, simulator, level, analysis
    out/<level>/<simulator>/<circuit>/<k>.npz       the signals of analysis k
    out/<level>/<simulator>/<circuit>/<k>.log       what the simulator printed

One line per finished circuit and simulator goes to the log as it happens.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import platform
import re
import resource
import shutil
import signal
import subprocess
import time
import tomllib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from .adapters import ADAPTERS, Adapter
from .circuit import Circuit, iter_circuits
from .entry import ROOT
from .stage import Compiler, StageError, stage, tail
from .translate import Untranslatable, translate

CONFIG = tomllib.loads((ROOT / "bench.toml").read_text(encoding="utf-8"))
LEVELS: dict[str, dict] = CONFIG["level"]


def _limits(memory: int):
    def apply():
        try:
            resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        except (ValueError, OSError):                   # macOS: no address-space limit
            pass
    return apply


def _cpu() -> str:
    """The processor model and the number of cores the run may use."""
    info = Path("/proc/cpuinfo")
    model = next((l.split(":", 1)[1].strip() for l in info.read_text().splitlines()
                  if l.startswith("model name")), "") if info.exists() else platform.processor()
    return f"{model}, {len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count()} cores"


def run_circuit(c: Circuit, ad: Adapter, level: str, work: Path, out: Path, compiler: Compiler,
                timeout: float, memory_gb: float, env: dict) -> list[dict]:
    base = {"circuit": c.name, "simulator": ad.name, "level": level, "version": ad.version()}
    nl = next((c.variants[d] for d in ad.dialects if d in c.variants), c.source)
    if nl.dialect not in ad.dialects:
        base["translated"] = nl.dialect
    dest = work / hashlib.sha1(f"{c.name}/{ad.name}/{level}".encode()).hexdigest()[:12]
    shutil.rmtree(dest, ignore_errors=True)
    keep = out / level / ad.name / c.name
    keep.mkdir(parents=True, exist_ok=True)
    records = []
    try:
        try:
            # A body staged for translation keeps its OSDI loads; the translation maps a
            # Verilog-A model onto one built into the target or rejects it.
            translated = "translated" in base
            netlist, osdi = stage(c.case, nl, dest, ad.osdi or translated, compiler, ad.name)
            ad.preload(netlist.parent, osdi if ad.osdi or not translated else [])
        except (StageError, NotImplementedError) as e:
            return [base | {"status": "stage-failed", "message": str(e)}]
        if translated:
            try:
                translate(c.case, nl, dest, ad.dialects[0], {a["type"] for a in c.analyses})
            except Untranslatable as e:
                return [base | {"status": "untranslated", "message": str(e)}]
        text = netlist.read_bytes().decode("latin-1")
        c = c.at(LEVELS[level])
        for k, a in enumerate(c.analyses):
            rec = base | {"analysis": k, "type": a["type"]}
            deck = netlist.with_name(f"{netlist.stem}.circref{k}.cir")
            rawfile = deck.with_suffix(".raw")
            try:
                deck.write_bytes(ad.deck(c, text, a, rawfile.name).encode("latin-1"))
            except NotImplementedError as e:            # an analysis the simulator lacks
                records.append(rec | {"status": "unsupported", "message": str(e)})
                continue
            t0 = time.monotonic()
            proc = subprocess.Popen(ad.argv(deck.name, rawfile.name), cwd=netlist.parent,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, start_new_session=True, env=env,
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
            elif rc or not rawfile.exists() or (ad.error and re.search(ad.error, log, re.M)):
                bad = ad.error and re.search(ad.error, log, re.M)
                rec |= {"status": "failed", "exit": rc,
                        "message": bad.group(0).strip() if bad else tail(log)}
            else:
                try:
                    signals = ad.read(rawfile, a)
                except Exception as e:
                    rec |= {"status": "failed", "message": f"output: {type(e).__name__}: {e}"}
                else:
                    if a["type"] == "op":                   # one point: an axis of its own
                        signals = {"op": np.zeros(1)} | {n: v[-1:] for n, v in signals.items()
                                                         if n[:2] in ("v(", "i(")}
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


def run(circuits: list[Circuit], adapters: list[Adapter], levels: list[str], out: Path,
        workers: int, timeout: float, memory_gb: float, threads: int = 1,
        shard: tuple[int, int] = (0, 1)) -> int:
    """``threads``: what every simulator may use per run (OpenMP, SANE), the same for all."""
    env = os.environ | {k: str(threads) for k in ("OMP_NUM_THREADS", "SANE_THREADS",
                                                  "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")}
    jobs = [(c, a, lv) for c in circuits for a in adapters for lv in levels]
    jobs = jobs[shard[0]::shard[1]]
    out.mkdir(parents=True, exist_ok=True)
    (out / "run.json").write_text(json.dumps({"threads": threads, "timeout_s": timeout,
                                              "memory_gb": memory_gb, "workers": workers,
                                              "cpu": _cpu()}))
    work = Path(os.environ.get("CIRCREF_WORK", "/scratch/circref"))
    compiler = Compiler(out / "osdi")
    counts: dict[str, int] = {}
    t0 = time.monotonic()
    with open(out / "results.jsonl", "a") as results, ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(run_circuit, c, a, lv, work, out, compiler, timeout, memory_gb,
                               env): (c, a, lv) for c, a, lv in jobs}
        for done, f in enumerate(as_completed(futures), 1):
            c, a, lv = futures[f]
            try:
                recs = f.result()
            except Exception as e:                  # a bug in circref, not in the circuit
                recs = [{"circuit": c.name, "simulator": a.name, "level": lv, "status": "error",
                         "message": f"{type(e).__name__}: {e}"}]
            for r in recs:
                results.write(json.dumps(r) + "\n")
                counts[r["status"]] = counts.get(r["status"], 0) + 1
            results.flush()
            status = ",".join(r["status"] for r in recs)
            wall = sum(r.get("wall_s", 0) for r in recs)
            msg = next((r["message"] for r in recs if "message" in r), "").replace("\n", " ")[:100]
            print(f"[{done}/{len(jobs)} {time.monotonic() - t0:6.0f}s] {a.name:10s} {lv:9s} {status:14s} "
                  f"{wall:8.2f}s {c.name}  {msg}", flush=True)
    print(" ".join(f"{k}={v}" for k, v in sorted(counts.items())), flush=True)
    return 0
