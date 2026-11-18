"""Run one deck on SANE: ``python run.py deck.cir out.raw``.

The deck is what the ngspice adapter writes: a SPICE body, an ``.options`` line, a
``.save`` line and one analysis line. SANE reads the body; this reads the rest with
circref's own parser, calls the matching analysis and writes a rawfile. It prints the
compile time (netlist to model) and the analysis time on lines of their own.
"""
from __future__ import annotations

import re
import sys
import time

import numpy as np
import sane

from circref import raw
from circref.adapters import body
from circref.circuit import Unsupported, lines, number, spice_analysis


def frequencies(a: dict) -> np.ndarray:
    if a["sweep"] == "lin":
        return np.linspace(a["start"], a["stop"], a["points"])
    base = 10.0 if a["sweep"] == "dec" else 2.0
    n = int(np.floor(np.log(a["stop"] / a["start"]) / np.log(base) * a["points"] + 1e-9)) + 1
    return a["start"] * base ** (np.arange(n) / a["points"])


def ac_input(text: str) -> tuple[str, complex]:
    """The first source with an AC magnitude, and its phasor."""
    for line in lines(text):
        tokens = line.replace("(", " ").replace(")", " ").split()
        if tokens[0][0] in "vi" and "ac" in tokens[3:]:
            k = tokens.index("ac", 3)
            mag, phase = 1.0, 0.0
            try:
                mag = number(tokens[k + 1])
                phase = number(tokens[k + 2])
            except (IndexError, Unsupported):
                pass
            return tokens[0], mag * np.exp(1j * np.radians(phase))
    raise SystemExit("ac: no source with an ac magnitude")


def main(deck: str, rawfile: str) -> int:
    text = open(deck, encoding="latin-1").read()
    analysis, outputs, options = None, [], {}
    for line in lines(text):
        head, *args = line[1:].split() if line.startswith(".") else ("", )
        if head in ("op", "dc", "ac", "tran"):
            analysis = spice_analysis(head, args)
        elif head == "save":
            outputs = args
        elif head == "options":
            options = {k: v for k, _, v in (a.partition("=") for a in args) if v}
    t0 = time.perf_counter()
    model = sane.Model.from_netlist("\n".join(body(text)) + "\n")
    names = {n.lower(): n for n in [*model.unknowns(), *model.node_names()]}
    if not outputs:
        outputs = [f"v({n.lower()})" for n in model.node_names()]

    def ref(sig: str) -> list[str] | None:
        kind, args = sig[0], sig[2:-1].split(",")
        if kind == "v":
            found = [names.get(a) for a in args]
            return found if all(found) else None
        for form in (f"i({args[0]})", f"{args[0]}#branch", args[0]):
            if form in names:
                return [names[form]]
        return None

    refs = {s: r for s in outputs if (r := ref(s))}
    pt = model.at()
    print(f"compile time (seconds) = {time.perf_counter() - t0:.6g}", flush=True)
    t0 = time.perf_counter()
    kind = analysis["type"]
    if kind == "op":
        op = pt.operating_point()
        axis, get = ("sweep", np.zeros(1)), lambda r: np.array([op[r]])
    elif kind == "dc":
        if len(analysis["sweep"]) != 1:
            raise SystemExit("dc: nested sweeps not wired yet")
        s = analysis["sweep"][0]
        params = {p.lower(): p for p in model.params()}
        param = next((params[c] for c in (s["source"], f"{s['source']}.dc", f"{s['source']}.v")
                      if c in params), None)
        if param is None:
            raise SystemExit(f"dc: no parameter for source {s['source']}")
        values = np.arange(s["start"], s["stop"] + s["step"] / 2, s["step"])
        sweep = pt.dc_sweep(param, values)
        axis, get = (f"v({s['source']})", values), lambda r: np.asarray(sweep[r])
    elif kind == "ac":
        source, phasor = ac_input(text)
        f = frequencies(analysis)
        resp = pt.ac(names.get(source, source), sorted({r for rs in refs.values() for r in rs}), f)
        axis, get = ("frequency", f), lambda r: phasor * np.asarray(resp[r])
    else:
        t = np.arange(0.0, analysis["stop"] + analysis["step"] / 2, analysis["step"])
        kw = {}
        if "reltol" in options:
            kw["rtol"] = number(options["reltol"])
        if "max_step" in analysis:
            kw["dt_max"] = analysis["max_step"]
        tr = pt.transient(t, **kw)
        keep = t >= analysis.get("start", 0.0)
        axis, get = ("time", np.asarray(tr.t)[keep]), lambda r: np.asarray(tr[r])[keep]
    signals = {axis[0]: axis[1]}
    for sig, rs in refs.items():
        signals[sig] = get(rs[0]) - (get(rs[1]) if len(rs) > 1 else 0)
    print(f"Total analysis time (seconds) = {time.perf_counter() - t0:.6g}", flush=True)
    open(rawfile, "wb").write(raw.write(kind, signals))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
