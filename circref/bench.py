"""Run circuits on simulators: every analysis of a circuit on every adapter that can read
its body, at every precision level of bench.toml, under a time and memory limit, signals
and timings kept.

    out/results.jsonl                               one line per circuit, simulator, level, analysis
    out/<level>/<simulator>/<circuit>/<k>.npz       the signals of analysis k
    out/<level>/<simulator>/<circuit>/<k>.log       what the simulator printed

One line per finished circuit and simulator goes to the log as it happens. Every job runs
in a process of its own, so a worker that dies takes only its own job. A run into an
``out`` that has records runs only the jobs without one; records of a circref error go
and their jobs run again.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import platform
import re
import resource
import selectors
import shutil
import signal
import subprocess
import sys
import time
import tomllib
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np

from .adapters import ADAPTERS, Adapter
from .circuit import Circuit, iter_circuits, load_circuit
from .entry import ROOT
from .stage import Compiler, StageError, stage, tail
from .translate import Untranslatable, translate

CONFIG = tomllib.loads((ROOT / "bench.toml").read_text(encoding="utf-8"))
LEVELS: dict[str, dict] = CONFIG["level"]
WORK = Path(os.environ.get("CIRCREF_WORK", "/scratch/circref"))


def _limits(memory: int):
    """The limits of a simulator's process: its address space, and the size of a file it
    writes (``output_bytes``; beyond it the kernel stops it with SIGXFSZ)."""
    def apply():
        resource.setrlimit(resource.RLIMIT_FSIZE, (CONFIG["run"]["output_bytes"],) * 2)
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


def _output(proc: subprocess.Popen, timeout: float) -> tuple[str, bool]:
    """What the simulator prints until it exits or ``timeout`` passes, its first and last
    half of ``log_bytes`` and never more in memory: (output, timed out)."""
    half, fd = CONFIG["run"]["log_bytes"] // 2, proc.stdout.fileno()
    head, end, cut = bytearray(), bytearray(), 0
    deadline = time.monotonic() + timeout
    timed_out = False
    with selectors.DefaultSelector() as sel:
        sel.register(fd, selectors.EVENT_READ)
        while (left := deadline - time.monotonic()) > 0:
            if not sel.select(left):
                continue
            chunk = os.read(fd, 1 << 16)
            if not chunk:
                break
            n = min(len(chunk), half - len(head))
            head += chunk[:n]
            end += chunk[n:]
            if len(end) > half:
                cut += len(end) - half
                del end[:len(end) - half]
        try:
            proc.wait(max(deadline - time.monotonic(), 0))
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            timed_out = True
    proc.stdout.close()
    skipped = f"\n[... {cut} bytes ...]\n".encode() if cut else b""
    return (bytes(head) + skipped + bytes(end)).decode("latin-1"), timed_out


def _simulate(ad: Adapter, c: Circuit, text: str, a: dict, deck: Path, keep: Path, k: int,
              timeout: float, memory_gb: float, env: dict) -> dict:
    """One analysis on one simulator: the record, the signals in keep/<k>.npz."""
    rawfile = deck.with_suffix(".raw")
    try:
        deck.write_bytes(ad.deck(c, text, a, rawfile.name).encode("latin-1"))
    except NotImplementedError as e:                    # an analysis the simulator lacks
        return {"status": "unsupported", "message": str(e)}
    rec: dict = {}
    t0 = time.monotonic()
    proc = subprocess.Popen(ad.argv(deck.name, rawfile.name), cwd=deck.parent,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, start_new_session=True, env=env,
                            preexec_fn=_limits(int(memory_gb * 2**30)))
    log, timed_out = _output(proc, timeout)
    rec["wall_s"] = round(time.monotonic() - t0, 4)
    (keep / f"{k}.log").write_text(log)
    if ad.timing and (m := re.search(ad.timing, log)):
        rec["sim_s"] = float(m.group(1))
    rc = proc.returncode
    bad = ad.error and re.search(ad.error, log, re.M)
    if timed_out:
        return rec | {"status": "timeout"}
    if rc < 0:
        return rec | {"status": "killed", "exit": rc}
    if rc or not rawfile.exists() or bad:
        return rec | {"status": "failed", "exit": rc, "message": bad.group(0).strip() if bad else tail(log)}
    try:
        signals = ad.read(rawfile, a)
    except Exception as e:
        return rec | {"status": "failed", "message": f"output: {type(e).__name__}: {e}"}
    if a["type"] == "op":                               # one point: an axis of its own
        signals = {"op": np.zeros(1)} | {n: v[-1:] for n, v in signals.items() if n[:2] in ("v(", "i(")}
    np.savez_compressed(keep / f"{k}.npz", **signals)
    return rec | {"status": "ok", "points": len(next(iter(signals.values()), [])), "signals": len(signals)}


def run_circuit(path: Path, simulator: str, levels: list[str], work: Path, out: Path,
                timeout: float, memory_gb: float, env: dict) -> list[dict]:
    """Every analysis of a circuit on one simulator at every level: staged and translated
    once, a deck per level and analysis. Runs in a worker process."""
    c, ad = load_circuit(path), ADAPTERS[simulator]
    base = {"circuit": c.name, "simulator": ad.name, "version": ad.version()}
    nl = next((c.variants[d] for d in ad.dialects if d in c.variants), c.source)
    if nl.dialect not in ad.dialects:
        base["translated"] = nl.dialect
    each = lambda rec: [base | {"level": lv} | rec for lv in levels]
    dest = work / hashlib.sha1(f"{c.name}/{ad.name}".encode()).hexdigest()[:12]
    shutil.rmtree(dest, ignore_errors=True)
    try:
        try:
            # A body staged for translation keeps its OSDI loads; the translation maps a
            # Verilog-A model onto one built into the target or rejects it.
            translated = "translated" in base
            netlist, osdi = stage(c.case, nl, dest, ad.osdi or translated, Compiler(out / "osdi"), ad.name)
            ad.preload(netlist.parent, osdi if ad.osdi or not translated else [])
        except (StageError, NotImplementedError) as e:
            return each({"status": "stage-failed", "message": str(e)})
        if translated:
            try:
                translate(c.case, nl, dest, ad.dialects[0], {a["type"] for a in c.analyses})
            except Untranslatable as e:
                return each({"status": "untranslated", "message": str(e)})
        text = netlist.read_bytes().decode("latin-1")
        records = []
        for lv in levels:
            at = c.at(LEVELS[lv])
            keep = out / lv / ad.name / c.name
            keep.mkdir(parents=True, exist_ok=True)
            for k, a in enumerate(at.analyses):
                deck = netlist.with_name(f"{netlist.stem}.circref-{lv}-{k}.cir")
                records.append(base | {"level": lv, "analysis": k, "type": a["type"]} |
                               _simulate(ad, at, text, a, deck, keep, k, timeout, memory_gb, env))
        return records
    finally:
        shutil.rmtree(dest, ignore_errors=True)


def _job(path: Path, simulator: str, levels: list[str], out: Path, timeout: float,
         memory_gb: float, env: dict) -> list[dict]:
    """run_circuit in a process of its own."""
    p = subprocess.run([sys.executable, "-m", "circref.bench"], capture_output=True, text=True, env=env,
                       input=json.dumps([str(path), simulator, levels, str(out), timeout, memory_gb]))
    if p.returncode:
        raise RuntimeError(f"worker exit {p.returncode}: {tail(p.stderr)}")
    return json.loads(p.stdout.splitlines()[-1])


def select(patterns: list[str]) -> list[Circuit]:
    return [c for c in iter_circuits()
            if not patterns or any(fnmatch.fnmatch(c.name, p) for p in patterns)]


def run(circuits: list[Circuit], adapters: list[Adapter], levels: list[str], out: Path,
        workers: int, timeout: float, memory_gb: float, threads: int = 1,
        shard: tuple[int, int] = (0, 1)) -> int:
    """A job per circuit and simulator, ``workers`` at a time. ``threads``: what every
    simulator may use per run (OpenMP), the same for all."""
    env = os.environ | {k: str(threads) for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                                                  "MKL_NUM_THREADS")}
    out.mkdir(parents=True, exist_ok=True)
    results = out / "results.jsonl"
    kept = [r for r in map(json.loads, results.read_text().splitlines() if results.exists() else [])
            if r["status"] != "error"]
    results.write_text("".join(json.dumps(r) + "\n" for r in kept))
    done = {(r["circuit"], r["simulator"], r["level"]) for r in kept}
    jobs = [(c, a) for c in circuits for a in adapters
            if any((c.name, a.name, lv) not in done for lv in levels)][shard[0]::shard[1]]
    (out / "run.json").write_text(json.dumps({"threads": threads, "timeout_s": timeout,
                                              "memory_gb": memory_gb, "workers": workers,
                                              "levels": levels, "cpu": _cpu()}))
    counts: Counter = Counter()
    t0 = time.monotonic()
    with open(results, "a") as log, ThreadPoolExecutor(workers) as pool:
        futures = {pool.submit(_job, c.path, a.name, levels, out, timeout, memory_gb, env): (c, a)
                   for c, a in jobs}
        for done, f in enumerate(as_completed(futures), 1):
            c, a = futures[f]
            try:
                recs = f.result()
            except Exception as e:                  # a bug in circref, not in the circuit
                recs = [{"circuit": c.name, "simulator": a.name, "level": lv, "status": "error",
                         "message": f"{type(e).__name__}: {e}"} for lv in levels]
            for r in recs:
                log.write(json.dumps(r) + "\n")
            log.flush()
            mine = Counter(r["status"] for r in recs)
            counts += mine
            wall = sum(r.get("wall_s", 0) for r in recs)
            msg = next((r["message"] for r in recs if "message" in r), "").replace("\n", " ")[:100]
            print(f"[{done}/{len(jobs)} {time.monotonic() - t0:6.0f}s] {a.name:10s} "
                  f"{' '.join(f'{k}={v}' for k, v in sorted(mine.items())):24s} {wall:8.2f}s {c.name}  {msg}",
                  flush=True)
    print(" ".join(f"{k}={v}" for k, v in sorted(counts.items())), flush=True)
    return 0


if __name__ == "__main__":                              # a job of run()
    path, simulator, levels, out, timeout, memory_gb = json.loads(sys.stdin.read())
    print(json.dumps(run_circuit(Path(path), simulator, levels, WORK, Path(out), timeout, memory_gb,
                                 dict(os.environ))))
