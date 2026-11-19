"""Plots of a run, from what run and compare left in its directory:

    plots/status.png        runs per simulator and status, a panel per level
    plots/references.png    analyses per type and reference status
    plots/accuracy.png      analyses within an error of the reference, per simulator, a panel per level
    plots/time.png          analyses within a time of the fastest simulator, per simulator
    plots/work.png          error against time of every run, a panel per simulator
    plots/circuits/<circuit>-<k>.png   one analysis: signal of every simulator, error over the axis

A run's error is never below the error of its reference: there it is plotted at that error.
"""
from __future__ import annotations

import fnmatch
import json
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
import matplotlib.ticker

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from .adapters import ADAPTERS  # noqa: E402
from .bench import CONFIG, LEVELS  # noqa: E402
from .compare import _load, error  # noqa: E402

P = CONFIG["plot"]
STYLE = {"figure.facecolor": P["surface"], "axes.facecolor": P["surface"], "savefig.facecolor": P["surface"],
         "axes.edgecolor": P["muted"], "axes.labelcolor": P["ink"], "text.color": P["ink"],
         "xtick.color": P["muted"], "ytick.color": P["muted"], "axes.grid": True, "grid.color": P["grid"],
         "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False, "font.size": 9,
         "legend.frameon": False, "lines.linewidth": 2, "axes.axisbelow": True}
TINY = 1e-16                                            # an error of 0 on a log axis


def _log(axis) -> None:
    """A log axis with at most six labeled decades."""
    axis.set_major_locator(matplotlib.ticker.LogLocator(base=10, numticks=6))
    axis.set_minor_locator(matplotlib.ticker.NullLocator())


def color(sim: str) -> tuple[str, str]:
    """(color, line style) of a simulator: fixed by its place in ADAPTERS."""
    k = list(ADAPTERS).index(sim) if sim in ADAPTERS else len(ADAPTERS)
    return P["series"][k % len(P["series"])], "-" if k < len(P["series"]) else "--"


def _sims(names) -> list[str]:
    order = list(ADAPTERS)
    return sorted(set(names), key=lambda s: (order.index(s) if s in order else len(order), s))


def _bars(ax, rows: list[str], segments: dict[str, dict[str, int]], colors: dict[str, str]) -> None:
    """Horizontal stacked bars, a row per entry, segments in the order of ``colors``."""
    y = np.arange(len(rows))
    left = np.zeros(len(rows))
    for seg, c in colors.items():
        w = np.array([segments[r].get(seg, 0) for r in rows], float)
        if w.any():
            ax.barh(y, w, left=left, color=c, edgecolor=P["surface"], linewidth=1, label=seg, height=0.7)
        left += w
    ax.set_yticks(y, rows)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)


def status(results: list[dict], path: Path) -> None:
    levels = [lv for lv in LEVELS if any(r.get("level") == lv for r in results)]
    sims = _sims(r["simulator"] for r in results)
    fig, axes = plt.subplots(1, len(levels), figsize=(3.6 * len(levels), 0.35 * len(sims) + 1.4),
                             sharey=True, squeeze=False)
    for ax, lv in zip(axes[0], levels):
        seg = {s: Counter(r["status"] for r in results if r["simulator"] == s and r.get("level") == lv)
               for s in sims}
        _bars(ax, sims, seg, P["status"])
        ax.set_title(f"level {lv}")
        ax.set_xlabel("runs (analyses, or circuits not staged)")
    handles, labels = {}, {}
    for ax in axes[0]:
        for h, lab in zip(*ax.get_legend_handles_labels()):
            handles[lab] = h
    fig.legend([handles[k] for k in P["status"] if k in handles], [k for k in P["status"] if k in handles],
               loc="upper center", ncol=len(handles), bbox_to_anchor=(0.5, 1.0))
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def references(refs: list[dict], path: Path) -> None:
    types = [t for t in ("op", "dc", "ac", "tran") if any(r["type"] == t for r in refs)]
    seg = {t: Counter(r["status"] for r in refs if r["type"] == t) for t in types}
    fig, ax = plt.subplots(figsize=(7, 0.4 * len(types) + 1.6))
    _bars(ax, types, seg, P["reference_status"])
    ax.set_xlabel("analyses run by at least one simulator")
    ax.legend(loc="upper center", ncol=len(P["reference_status"]), bbox_to_anchor=(0.5, 1.25))
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _floored(r: dict) -> float:
    return max(r["error"], r["reference_error"] or 0, TINY)


def _cumulative(ax, values: dict[str, list[float]]) -> None:
    for s, v in values.items():
        if v:
            x = np.sort(v)
            c, ls = color(s)
            ax.step(np.concatenate([[x[0]], x]), np.arange(len(x) + 1), where="post", color=c, ls=ls, label=s)


def accuracy(rows: list[dict], path: Path) -> None:
    levels = [lv for lv in LEVELS if any(r["level"] == lv for r in rows)]
    sims = _sims(r["simulator"] for r in rows)
    fig, axes = plt.subplots(1, len(levels), figsize=(4.2 * len(levels), 3.6), sharey=True, squeeze=False)
    for ax, lv in zip(axes[0], levels):
        _cumulative(ax, {s: [_floored(r) for r in rows if r["simulator"] == s and r["level"] == lv
                             and r["error"] is not None and not r["outlier"]] for s in sims})
        ax.set_xscale("log")
        _log(ax.xaxis)
        ax.set_title(f"level {lv}")
        ax.set_xlabel("error against the reference (relative to peak)")
    axes[0][0].set_ylabel("analyses with at most this error")
    axes[0][-1].legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def _fastest(rows: list[dict], level: str) -> dict[tuple, float]:
    best: dict[tuple, float] = {}
    for r in rows:
        if r["level"] == level and r["wall_s"]:
            k = (r["circuit"], r["analysis"])
            best[k] = min(best.get(k, np.inf), r["wall_s"])
    return best


def time(rows: list[dict], results: list[dict], path: Path) -> None:
    """Default level, every ok run of an analysis that two or more simulators finished."""
    ok = [r for r in results if r["status"] == "ok" and r.get("level") == "default" and r.get("wall_s")]
    by = defaultdict(list)
    for r in ok:
        by[(r["circuit"], r["analysis"])].append(r)
    ratios = defaultdict(list)
    for runs in by.values():
        if len(runs) > 1:
            t0 = min(r["wall_s"] for r in runs)
            for r in runs:
                ratios[r["simulator"]].append(r["wall_s"] / t0)
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    _cumulative(ax, {s: ratios[s] for s in _sims(ratios)})
    ax.set_xscale("log")
    ax.set_xlabel("wall time against the fastest simulator on the same analysis, level default")
    ax.set_ylabel("analyses within this time")
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def work(rows: list[dict], path: Path) -> None:
    """Every run with an error: error against wall time over the fastest run of any
    simulator at the default level; the median of each level as a large mark."""
    rows = [r for r in rows if r["error"] is not None and not r["outlier"] and r["wall_s"]]
    best = _fastest(rows, "default")
    sims = _sims(r["simulator"] for r in rows)
    if not sims:
        return
    cols = min(3, len(sims))
    nrows = -(-len(sims) // cols)
    fig, axes = plt.subplots(nrows, cols, figsize=(3.8 * cols, 3.2 * nrows), sharex=True, sharey=True,
                             squeeze=False)
    lc = dict(zip(LEVELS, P["series"]))
    for ax, s in zip(axes.flat, sims):
        for lv in LEVELS:
            pts = [(_floored(r), r["wall_s"] / best[(r["circuit"], r["analysis"])]) for r in rows
                   if r["simulator"] == s and r["level"] == lv and (r["circuit"], r["analysis"]) in best]
            if not pts:
                continue
            e, t = np.array(pts).T
            ax.scatter(e, t, s=10, color=lc[lv], alpha=0.5, linewidths=0)
            ax.scatter([np.median(e)], [np.exp(np.mean(np.log(t)))], s=70, color=lc[lv],
                       edgecolors=P["surface"], linewidths=2, label=lv, zorder=3)
        ax.set_title(s)
        ax.set_xscale("log")
        ax.set_yscale("log")
        _log(ax.xaxis)
    for ax in axes.flat[len(sims):]:
        ax.set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("error against the reference")
    for ax in axes[:, 0]:
        ax.set_ylabel("wall time / fastest at default")
    handles = [plt.Line2D([], [], marker="o", ls="", color=lc[lv], markersize=7) for lv in LEVELS]
    fig.legend(handles, [f"level {lv} (large: median error, geometric mean time)" if i == 0 else f"level {lv}"
                         for i, lv in enumerate(LEVELS)], loc="upper center", ncol=len(LEVELS))
    fig.tight_layout(rect=(0, 0, 1, 1 - 0.35 / (3.2 * nrows)))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def circuit(out: Path, recs: list[dict], info: dict, ref, path: Path) -> None:
    """One analysis at the default level: the signal most often worst, of every simulator
    and the reference; below, each simulator's difference to the reference."""
    runs = {r["simulator"]: _load(out, r) for r in recs if r["level"] == "default"}
    if not runs:
        return
    worst = Counter(e[1] for s, run in runs.items() if ref and (e := error(run, ref)))
    shared = set.intersection(*(set(y) for _, y in runs.values()))
    sig = worst.most_common(1)[0][0] if worst else min(shared, default=None)
    if sig is None:
        return
    fig, axes = plt.subplots(2 if ref else 1, 1, figsize=(7, 5 if ref else 3), sharex=True, squeeze=False)
    top = axes[0][0]
    a = recs[0]
    part = np.abs if a["type"] == "ac" else np.real
    for s in _sims(runs):
        x, y = runs[s]
        if sig in y:
            c, ls = color(s)
            top.plot(x, part(y[sig]), color=c, ls=ls, lw=1.2, label=s)
    if ref and sig in ref[1]:
        top.plot(ref[0], part(ref[1][sig]), color=P["reference"], ls=":", lw=1.2,
                 label=f"reference ({info['status']}: {', '.join(info['simulators'])})")
    top.set_ylabel(("|%s|" if a["type"] == "ac" else "%s") % sig)
    top.set_title(f"{a['circuit']}  analysis {a['analysis']} ({a['type']}), level default")
    top.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0))
    if ref and sig in ref[1]:
        bot = axes[1][0]
        xf, yf = ref[0], ref[1][sig]
        scale = np.max(np.abs(yf)) + CONFIG["compare"]["floor"][sig[0]]
        o = np.argsort(xf, kind="stable")
        for s in _sims(runs):
            x, y = runs[s]
            if sig not in y or len(xf) < 2:
                continue
            inside = (x >= xf.min()) & (x <= xf.max())
            at = np.interp(x[inside], xf[o], yf.real[o]) + (
                1j * np.interp(x[inside], xf[o], yf.imag[o]) if np.iscomplexobj(yf) else 0)
            c, ls = color(s)
            bot.plot(x[inside], np.maximum(np.abs(y[sig][inside] - at) / scale, TINY), color=c, ls=ls, lw=1)
        bot.set_yscale("log")
        bot.set_ylabel("difference / peak")
    axes[-1][0].set_xlabel({"tran": "time (s)", "ac": "frequency (Hz)", "dc": "sweep", "op": ""}[a["type"]])
    if a["type"] == "ac":
        for ax in axes[:, 0]:
            ax.set_xscale("log")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot(out: Path, circuits: list[str] = ()) -> list[Path]:
    """The plots of the run in ``out``; ``circuits``: names or globs whose analyses get a
    plot of their own (compare.json from ``compare`` first)."""
    plt.rcParams.update(STYLE)
    results = [json.loads(l) for l in (out / "results.jsonl").read_text().splitlines()]
    data = json.loads((out / "compare.json").read_text())
    d = out / "plots"
    d.mkdir(exist_ok=True)
    status(results, d / "status.png")
    references(data["references"], d / "references.png")
    accuracy(data["rows"], d / "accuracy.png")
    time(data["rows"], results, d / "time.png")
    work(data["rows"], d / "work.png")
    if circuits:
        from .compare import reference
        (d / "circuits").mkdir(exist_ok=True)
        by = defaultdict(list)
        for r in results:
            if r["status"] == "ok" and any(fnmatch.fnmatch(r["circuit"], p) for p in circuits):
                by[(r["circuit"], r["analysis"])].append(r)
        for (c, k), recs in sorted(by.items()):
            info, ref = reference({(r["simulator"], r["level"]): _load(out, r) for r in recs})
            circuit(out, [r | {"analysis": k} for r in recs], info, ref, d / "circuits" / f"{c}-{k}.png")
    return sorted(d.rglob("*.png"))
