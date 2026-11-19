"""Simulators against a reference: for every circuit and analysis the reference its
converged runs give, and the error of every run against it, with the time it took.

A simulator's run at the reference level is converged when its run at the fine level is
within ``converged`` of it. The reference of an analysis is the median of the converged
reference runs of all simulators over the signals they share; while they differ from it
by more than ``agree``, the one furthest off is set aside (an outlier: a different model
or circuit, not a numerical error), as long as two remain. Two that disagree give no
reference. The error the reference carries: the largest convergence and agreement
deviation it rests on.

The error of a run: over the signals it shares with the reference, the largest difference
on the run's own points (its time steps, its sweep points) to the reference there,
relative to the reference signal's peak plus a floor. Bounds in bench.toml.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from .bench import CONFIG

C = CONFIG["compare"]
Run = tuple[np.ndarray, dict[str, np.ndarray]]          # axis, signals on it


def _load(out: Path, rec: dict) -> Run:
    with np.load(out / rec["level"] / rec["simulator"] / rec["circuit"] / f"{rec['analysis']}.npz") as d:
        axis, *names = d.files
        return np.real(d[axis]), {n: d[n] for n in names
                                  if n[:2] in ("v(", "i(") and len(d[n]) == len(d[axis])}


def _on(ax: np.ndarray, y: np.ndarray, x: np.ndarray) -> np.ndarray | None:
    """``y`` over ``ax`` at the points ``x``: the values where the axes are one, linear
    between points on a monotonic axis, none on nested sweeps."""
    if len(ax) == len(x) and np.allclose(ax, x, rtol=1e-9, atol=0):
        return y
    d = np.diff(ax)
    if len(ax) < 2 or not (np.all(d >= 0) or np.all(d <= 0)):
        return None
    o = np.argsort(ax, kind="stable")
    re_ = np.interp(x, ax[o], y.real[o])
    return re_ + 1j * np.interp(x, ax[o], y.imag[o]) if np.iscomplexobj(y) else re_


def error(run: Run, ref: Run) -> tuple[float, str] | None:
    """(largest relative difference of ``run`` to ``ref``, the signal it is on)."""
    (xr, yr), (xf, yf) = run, ref
    inside = (xr >= xf.min()) & (xr <= xf.max())
    worst = None
    for s in sorted(yr.keys() & yf.keys()):
        at = _on(xf, yf[s], xr[inside])
        if at is None or not inside.any():
            continue
        e = float(np.max(np.abs(yr[s][inside] - at)) / (np.max(np.abs(yf[s])) + C["floor"][s[0]]))
        if worst is None or e > worst[0]:
            worst = (e, s)
    return worst


def _median(runs: dict[str, Run]) -> Run | None:
    """The median of runs on the axis of the one with the most points, over their shared signals."""
    x = max(runs.values(), key=lambda r: len(r[0]))[0]
    shared = set.intersection(*(set(y) for _, y in runs.values()))
    med = {}
    for s in sorted(shared):
        on = [_on(ax, y[s], x) for ax, y in runs.values()]
        if any(v is None for v in on):
            continue
        st = np.array(on)
        med[s] = np.median(st.real, 0) + (1j * np.median(st.imag, 0) if np.iscomplexobj(st) else 0)
    return (x, med) if med else None


def reference(runs: dict[tuple[str, str], Run]) -> tuple[dict, Run | None]:
    """The reference of one analysis from its runs by (simulator, level)."""
    conv = {}
    for (s, lv), r in runs.items():
        if lv == "reference" and (s, "fine") in runs:
            e = error(runs[(s, "fine")], r)
            if e is not None and e[0] <= C["converged"]:
                conv[s] = e[0]
    if not conv:
        return {"status": "none"}, None
    cands = {s: runs[(s, "reference")] for s in conv}
    outliers: list[str] = []
    while True:
        med = cands[next(iter(cands))] if len(cands) == 1 else _median(cands)
        if med is None:
            return {"status": "no shared signal", "simulators": sorted(cands)}, None
        dev = {s: (error(r, med) or (np.inf, None))[0] for s, r in cands.items()}
        off = max(dev, key=dev.get)
        if dev[off] <= C["agree"]:
            break
        if len(cands) == 2:
            return {"status": "disagree", "simulators": sorted(cands),
                    "deviation": dev[off], "outliers": outliers}, None
        outliers.append(off)
        del cands[off]
    info = {"status": "agreed" if len(cands) > 1 else "single", "simulators": sorted(cands),
            "outliers": outliers, "error": max([conv[s] for s in cands] + list(dev.values()))}
    return info, med


def compare(out: Path) -> dict:
    by_run: dict[tuple, list[dict]] = defaultdict(list)
    for line in (out / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        if r["status"] == "ok":
            by_run[(r["circuit"], r["analysis"])].append(r)
    refs, rows = [], []
    for (circuit, k), recs in sorted(by_run.items()):
        runs = {(r["simulator"], r["level"]): _load(out, r) for r in recs}
        info, ref = reference(runs)
        refs.append({"circuit": circuit, "analysis": k, "type": recs[0]["type"]} | info)
        for r in recs:
            e = error(runs[(r["simulator"], r["level"])], ref) if ref else None
            rows.append({"circuit": circuit, "analysis": k, "type": r["type"],
                         "simulator": r["simulator"], "level": r["level"],
                         "error": e[0] if e else None, "worst_signal": e[1] if e else None,
                         "reference_error": info.get("error"),
                         "outlier": r["simulator"] in info.get("outliers", []),
                         "wall_s": r.get("wall_s"), "sim_s": r.get("sim_s")})
    return {"references": refs, "rows": rows}


def write(out: Path) -> dict:
    """compare() of the run in ``out``, into out/compare.json."""
    result = compare(out)
    (out / "compare.json").write_text(json.dumps(result))
    return result
