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


def _table(head: list[str], rows: list[list]) -> list[str]:
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + \
           ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]


def summary(out: Path) -> str:
    """Status per simulator and level; references; accuracy at the default level; the
    time each simulator takes to reach an accuracy. Writes out/compare.json."""
    status: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    versions: dict[str, str] = {}
    for line in (out / "results.jsonl").read_text().splitlines():
        r = json.loads(line)
        status[(r["simulator"], r.get("level", ""))][r["status"]] += 1
        versions[r["simulator"]] = r.get("version") or versions.get(r["simulator"], "")
    names = sorted({k for v in status.values() for k in v})
    lines = _table(["simulator", "version", "level"] + names,
                   [[s, versions[s], lv] + [status[(s, lv)].get(n, "") for n in names]
                    for s, lv in sorted(status)])
    result = compare(out)
    (out / "compare.json").write_text(json.dumps(result))
    refs, rows = result["references"], result["rows"]

    kinds = ["agreed", "single", "disagree", "none", "no shared signal"]
    by_type = defaultdict(lambda: defaultdict(int))
    for r in refs:
        by_type[r["type"]][r["status"]] += 1
    lines += ["", "references per analysis: agreed by several converged simulators, from a single one, "
              "two converged that disagree, none converged:", ""]
    lines += _table(["type"] + kinds + ["median error"],
                    [[t] + [by_type[t].get(k, "") for k in kinds] +
                     [f"{np.median([r['error'] for r in refs if r['type'] == t and 'error' in r] or [np.nan]):.1e}"]
                     for t in sorted(by_type)])

    sims = sorted({r["simulator"] for r in rows})
    bands = C["bands"]
    lines += ["", "error against the reference at the default level, per analysis (worst signal); "
              "outlier: its reference run disagrees with the others:", ""]
    table = []
    for s in sims:
        mine = [r for r in rows if r["simulator"] == s and r["level"] == "default" and r["error"] is not None]
        good = [r for r in mine if not r["outlier"]]
        cells = [len(mine), sum(r["error"] <= r["reference_error"] for r in good)]
        lo = -1.0
        for b in bands:
            cells.append(sum(lo < r["error"] <= b and r["error"] > r["reference_error"] for r in good))
            lo = b
        table.append([s] + cells + [sum(r["error"] > bands[-1] for r in good), len(mine) - len(good)])
    lines += _table(["simulator", "analyses", "within reference error"] + [f"<= {b:g}" for b in bands] +
                    [f"> {bands[-1]:g}", "outlier"], table)

    # Work at a precision: per analysis the cheapest level that reaches the error, against
    # the fastest simulator that reaches it on the same analysis. Wall time of the run.
    lines += ["", "time to reach an error, against the fastest simulator that reaches it on the same "
              "analysis (geometric mean of wall time, cheapest level that reaches it):", ""]
    cheapest: dict[tuple, float] = {}
    for r in rows:
        if r["error"] is None or r["outlier"] or not r["wall_s"]:
            continue
        for b in bands:
            if max(r["error"], r["reference_error"]) <= b:
                key = (r["circuit"], r["analysis"], b, r["simulator"])
                cheapest[key] = min(cheapest.get(key, np.inf), r["wall_s"])
    fastest: dict[tuple, list[float]] = defaultdict(list)
    for (c, k, b, s), t in cheapest.items():
        fastest[(c, k, b)].append(t)
    table = []
    for s in sims:
        cells = []
        for b in bands:
            ratios = [t / min(fastest[(c, k, bb)]) for (c, k, bb, ss), t in cheapest.items()
                      if ss == s and bb == b and len(fastest[(c, k, bb)]) > 1]
            reached = sum(1 for (_, _, bb, ss) in cheapest if ss == s and bb == b)
            gm = f"{np.exp(np.mean(np.log(ratios))):.2f}" if ratios else "-"
            cells.append(f"{reached} / {gm}")
        table.append([s] + cells)
    lines += _table(["simulator"] + [f"<= {b:g}: reached / ratio" for b in bands], table)
    return "\n".join(lines)
