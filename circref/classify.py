"""Classes of a netlist, derived from what it contains, never stated.

size         tiny < 10 <= small < 100 <= medium < 1000 <= large < 10000 <= xl devices
linear       every device is linear (R, L, C, coupled L, independent and linear
             controlled sources, lossless and lossy lines): one linear solve per point
portability  core: op, dc, ac and tran on standard devices, what every SPICE runs once
                   the syntax is translated
             veriloga: as core, but a model has to be compiled from Verilog-A first
             specific: uses something only its own simulator (family) has, see reasons
"""
from __future__ import annotations

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
