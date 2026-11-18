"""Simulators against each other: for every circuit and analysis that two or more
simulators finished, every signal they share on one axis, each simulator's deviation from
the median of all, and the times.

The deviation of a signal is its largest difference to the median over the axis,
relative to the median's largest magnitude plus a floor (1 uV, 1 pA) that keeps signals
near zero from dominating. A transient is compared on ``points`` uniform time points,
DC and AC on the first simulator's sweep points.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

FLOOR = {"v": 1e-6, "i": 1e-12}
BANDS = (1e-6, 1e-4, 1e-2)


def _load(out: Path, rec: dict) -> dict[str, np.ndarray]:
    with np.load(out / rec["simulator"] / rec["circuit"] / f"{rec['analysis']}.npz") as d:
        return {k: d[k] for k in d.files}


def deviations(out: Path, recs: list[dict], points: int = 1001) -> dict[str, dict[str, float]]:
    """simulator -> signal -> relative deviation from the median, for one analysis."""
    data = {r["simulator"]: _load(out, r) for r in recs}
    axis_of = {s: next(iter(d)) for s, d in data.items()}
    shared = set.intersection(*({k for k in d if k != axis_of[s]} for s, d in data.items()))
    shared = {k for k in shared if k[:2] in ("v(", "i(")}
    if not shared:
        return {}
    kind = recs[0]["type"]
    first = next(iter(data))
    if kind == "tran":
        ends = [(d[axis_of[s]][0].real, d[axis_of[s]][-1].real) for s, d in data.items()]
        x = np.linspace(max(e[0] for e in ends), min(e[1] for e in ends), points)
    else:
        x = np.real(data[first][axis_of[first]])
    out_: dict[str, dict[str, float]] = defaultdict(dict)
    for sig in sorted(shared):
        curves = {}
        for s, d in data.items():
            ax, y = np.real(d[axis_of[s]]), d[sig]
            if len(ax) != len(y):
                continue
            if kind == "op" or len(ax) == 1:
                curves[s] = y[:1]
            elif kind == "tran" or len(ax) != len(x) or not np.allclose(ax, x, rtol=1e-9):
                if np.any(np.diff(ax) <= 0):                # nested sweeps: not interpolable
                    continue
                curves[s] = np.interp(x, ax, y.real) + (1j * np.interp(x, ax, y.imag)
                                                        if np.iscomplexobj(y) else 0)
            else:
                curves[s] = y
        if len(curves) < 2:
            continue
        stack = np.array(list(curves.values()))
        med = np.median(stack.real, 0) + (1j * np.median(stack.imag, 0) if np.iscomplexobj(stack) else 0)
        scale = np.max(np.abs(med)) + FLOOR[sig[0]]
        for s, y in curves.items():
            out_[s][sig] = float(np.max(np.abs(y - med)) / scale)
    return out_


def compare(out: Path) -> dict:
    by_run: dict[tuple, list[dict]] = defaultdict(list)
    for line in (out / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["status"] == "ok":
            by_run[(r["circuit"], r["analysis"])].append(r)
    rows = []
    for (circuit, k), recs in sorted(by_run.items()):
        if len({r["simulator"] for r in recs}) < 2:
            continue
        dev = deviations(out, recs)
        for r in recs:
            sig = dev.get(r["simulator"], {})
            worst = max(sig.items(), key=lambda kv: kv[1]) if sig else (None, None)
            rows.append({"circuit": circuit, "analysis": k, "type": r["type"],
                         "simulator": r["simulator"], "signals": len(sig),
                         "worst_signal": worst[0], "deviation": worst[1],
                         "wall_s": r.get("wall_s"), "sim_s": r.get("sim_s")})
    return {"rows": rows}


def summary(out: Path) -> str:
    """Status per simulator; agreement bands; time against the fastest per analysis."""
    status: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    versions: dict[str, str] = {}
    for line in (out / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        status[r["simulator"]][r["status"]] += 1
        versions[r["simulator"]] = r.get("version") or versions.get(r["simulator"], "")
    names = sorted({k for v in status.values() for k in v})
    lines = ["| simulator | version | " + " | ".join(names) + " |", "|---|---|" + "---|" * len(names)]
    for s in sorted(status):
        lines.append(f"| {s} | {versions[s]} | " + " | ".join(str(status[s].get(n, "")) for n in names) + " |")
    rows = compare(out)["rows"]
    if rows:
        lines += ["", "deviation from the median of the simulators, per analysis (worst signal):", "",
                  "| simulator | analyses | " + " | ".join(f"<= {b:g}" for b in BANDS) + f" | > {BANDS[-1]:g} | no shared signal |",
                  "|---|---|" + "---|" * (len(BANDS) + 2)]
        for s in sorted({r["simulator"] for r in rows}):
            mine = [r for r in rows if r["simulator"] == s]
            devs = [r["deviation"] for r in mine if r["deviation"] is not None]
            cells, lo = [], -1.0
            for b in BANDS:
                cells.append(sum(lo < d <= b for d in devs))
                lo = b
            cells += [sum(d > BANDS[-1] for d in devs), len(mine) - len(devs)]
            lines.append(f"| {s} | {len(mine)} | " + " | ".join(map(str, cells)) + " |")
        # time: each simulator's own analysis time, against the fastest on the same analysis
        best: dict[tuple, float] = {}
        for r in rows:
            t = r["sim_s"] or r["wall_s"]
            key = (r["circuit"], r["analysis"])
            best[key] = min(best.get(key, t), t)
        lines += ["", "time against the fastest simulator on the same analysis (geometric mean, own analysis time where reported):", "",
                  "| simulator | analyses | ratio | total s |", "|---|---|---|---|"]
        for s in sorted({r["simulator"] for r in rows}):
            ts = [((r["sim_s"] or r["wall_s"]), best[(r["circuit"], r["analysis"])]) for r in rows
                  if r["simulator"] == s]
            ratios = [t / b for t, b in ts if b > 0]
            gm = float(np.exp(np.mean(np.log(ratios)))) if ratios else float("nan")
            lines.append(f"| {s} | {len(ts)} | {gm:.2f} | {sum(t for t, _ in ts):.1f} |")
    return "\n".join(lines)
