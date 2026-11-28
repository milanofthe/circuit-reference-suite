"""Properties of a circuit: what its case states, and what is derived from the netlist,
never stated. ``properties`` is the row of a circuit in index.csv.

devices      leaf instances once every subcircuit is expanded, those of libraries too
nodes        distinct nodes but ground; empty where the terminals of an instance are not read
unknowns     nodes plus the branch currents of voltage-defined elements (V, L, E, H, two
             per line), without the internal nodes of device models
r ... other  devices by class (CLASSES)
models       the compact models of the semiconductor devices (d, q, j, m), as type/level

size         tiny < 10 <= small < 100 <= medium < 1000 <= large < 10000 <= xl devices
linear       every device is linear (R, L, C, coupled L, independent and linear
             controlled sources, lossless and lossy lines): one linear solve per point
portability  core: op, dc, ac and tran on standard devices, what every SPICE runs once
                   the syntax is translated
             veriloga: as core, but a model has to be compiled from Verilog-A first
             specific: uses something only its own simulator (family) has, see reasons
"""
from __future__ import annotations

import re

from .entry import Graph

SIZES = (("tiny", 10), ("small", 100), ("medium", 1000), ("large", 10000), ("xl", None))
CORE_ANALYSES = {"op", "dc", "ac", "tran"}
# Bookkeeping, not an analysis of its own.
NEUTRAL_ANALYSES = {"four", "step", "lin"}

LINEAR_SPICE = set("rlckvieefgh") | {"t", "o"}
LINEAR_TYPES = {"resistor", "capacitor", "inductor", "vsource", "isource", "vcvs", "vccs", "ccvs",
                "cccs", "mutual_inductor", "port", "sp_resistor", "sp_capacitor",
                "sp_inductor", "r", "c", "l", "vac", "vdc", "idc", "iac", "vpulse", "ipulse",
                "vrect", "irect", "vprobe", "iprobe", "tline", "mut", "spfile", "pac"}
CIDER = {"numd", "numd2", "numos", "nbjt", "nbjt2"}


def size(g: Graph) -> str:
    n = g.devices
    return next(name for name, limit in SIZES if limit is None or n < limit)


def linear(g: Graph) -> bool:
    for kind in g.kinds:
        if kind.startswith("x:"):
            master = kind[2:]
            if g.models.get(master, master) not in LINEAR_TYPES:
                return False
        elif g.dialect in ("josim", "wrspice") and kind == "b":
            return False                                    # Josephson junction
        elif kind not in LINEAR_SPICE and kind not in LINEAR_TYPES:
            return False
    return bool(g.kinds)


def portability(g: Graph) -> tuple[str, list[str]]:
    reasons = [f"analysis {a}" for a in sorted(set(g.analyses) - CORE_ANALYSES - NEUTRAL_ANALYSES)]
    kinds = set(g.kinds)
    if g.control:
        reasons.append(".control script")
    if "a" in kinds and g.dialect in ("ngspice", "spice3"):
        reasons.append("XSPICE code model")
    if CIDER & set(g.models.values()):
        reasons.append("CIDER numerical device")
    if g.dialect in ("josim", "wrspice") and "b" in kinds:
        reasons.append("Josephson junction")
    if g.dialect == "xyce" and kinds & {"y", "u"}:
        reasons.append("Xyce device (Y or digital U)")
    if reasons:
        return "specific", reasons + (["Verilog-A model"] if g.veriloga else [])
    if g.veriloga:
        return "veriloga", ["Verilog-A model"]
    return "core", []


# Device classes, the columns of index.csv: a SPICE letter, or for an instance of a named
# master (Spectre, Qucs, OSDI, Verilog-A) the type of its model by pattern.
CLASSES = ("r", "c", "l", "k", "v", "i", "ctrl", "b", "d", "q", "j", "m", "t", "s", "other")
LETTERS = {"r": "r", "c": "c", "l": "l", "k": "k", "v": "v", "i": "i", "e": "ctrl", "f": "ctrl",
           "g": "ctrl", "h": "ctrl", "b": "b", "d": "d", "q": "q", "j": "j", "z": "j", "m": "m",
           "t": "t", "o": "t", "s": "s", "w": "s"}
TYPES = [("q", r"npn|pnp|bjt|vbic|hicum|mextram|gummel|hbt"), ("d", r"diode|juncap|^d$"),
         ("j", r"jfet|^[np]jf$|mesfet"), ("m", r"mos|bsim|psp|hisim|ekv|cmg|fet"),
         ("k", r"mutual|^mut$"), ("ctrl", r"^(vcvs|vccs|ccvs|cccs)$"),
         ("r", r"^(r|res|resistor|sp_resistor)$"), ("c", r"^(c|cap|capacitor|sp_capacitor)$"),
         ("l", r"^(l|ind|inductor|sp_inductor)$"),
         ("v", r"^(v|vsource|vdc|vac|vpulse|vrect|port)$"),
         ("i", r"^(i|isource|idc|iac|ipulse|irect)$"),
         ("t", r"tline|tlin|transline|coax|mlin"), ("s", r"switch|^sw$|relay")]
# Elements whose branch current is an unknown of modified nodal analysis: SPICE letters
# and the primitives of the other dialects.
BRANCHES = {"v": 1, "l": 1, "e": 1, "h": 1, "e~": 1, "h~": 1, "t": 2, "o": 2, "vsource": 1,
            "inductor": 1, "sp_inductor": 1, "vcvs": 1, "ccvs": 1, "vdc": 1, "vac": 1,
            "vpulse": 1, "vrect": 1, "iprobe": 1, "tline": 2, "tlin": 2}


def _model(g: Graph, name: str) -> str | None:
    """A model name as type/level; binned models are name.1, name.2, ..."""
    if name not in g.models:
        name = next((m for m in g.models if m.startswith(name + ".")), name)
    if name not in g.models:
        return None
    return g.models[name] + (f"/{g.levels[name]}" if name in g.levels else "")


def _type(g: Graph, name: str | None) -> str:
    """The model type behind a name (binned models included), else the name itself."""
    m = _model(g, name) if name else None
    return m.split("/")[0] if m else (name or "")


def device_class(g: Graph, kind: str, model: str | None) -> str:
    """The class of a leaf: by its SPICE letter, else by the type of the model it names
    (OSDI N, Xyce Y) or of its master (Spectre, Qucs, Verilog-A)."""
    if kind.endswith("~"):
        return "b"
    if len(kind) == 1 and kind in LETTERS and g.dialect != "qucsator":
        return LETTERS[kind]
    t = _type(g, model or (kind[2:] if kind.startswith("x:") else kind))
    return next((c for c, pat in TYPES if re.search(pat, t)), "other")


def derived(g: Graph) -> dict:
    """The properties read from a netlist and what it pulls in."""
    flat = g.flat
    classes = dict.fromkeys(CLASSES, 0)
    branches = 0
    models = set()
    for (kind, model), n in flat.leaves.items():
        c = device_class(g, kind, model)
        classes[c] += n
        name = model or (kind[2:] if kind.startswith("x:") else kind)
        branches += n * BRANCHES.get(kind if len(kind) <= 2 else _type(g, name), 0)
        if c in ("d", "q", "j", "m") and name and (m := _model(g, name)):
            models.add(m)
    port, why = portability(g)
    return {"devices": g.devices, "nodes": flat.nodes,
            "unknowns": None if flat.nodes is None else flat.nodes + branches,
            **classes, "models": " ".join(sorted(models)),
            "linear": linear(g), "portability": port, "portability_reasons": "; ".join(why),
            "size": size(g)}


def properties(circuit) -> dict:
    """The row of a circuit in index.csv: what its case states, then ``derived``."""
    case, nl = circuit.case, circuit.source
    return {"name": circuit.name, "case": case.id, "source": nl.file, "dialect": nl.dialect,
            "family": case.family, "license": case.source["license"],
            "libraries": " ".join(sorted(case.graphs[nl.file].libraries)),
            "generated": nl.size,
            "analyses": " ".join(dict.fromkeys(a["type"] for a in circuit.analyses)),
            **derived(case.graphs[nl.file])}
