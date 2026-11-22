"""Generated cases: circuits written by a generator here instead of taken from upstream.

A generated case states its generator in case.toml (``[generator]``, and ``size`` per
netlist); its netlists are listed under files with provenance ``generated`` and the
sha256 of what the generator writes, so that a change of the generator fails check. They
are not committed (.gitignore): build writes them, and validate, check and run write the
ones that are missing.

A generator builds the circuit as a list of elements; one writer per dialect states them.
A pulsed source has the pulse's initial value ``v1`` as its DC value, so that every
simulator solves the operating point at it, whether it reads the DC value or the waveform
at t = 0, and the transient starts from that operating point.

``network``: an RC network, a capacitor ``c`` from every node to ground and a resistor
``r`` per edge of a graph, driven at node 1 through ``source_r`` by a pulse. Without
``diode`` it is linear: the operating point is one linear solve of the resistor network. With ``diode`` (the parameters of a junction
diode model) a diode goes from every node to ground: the operating point takes Newton
iterations, the matrix values change at every one of them, the graph and with it the
elimination structure stay. The networks differ only in the graph:

    ladder  a path of ``size`` nodes: the elimination tree is one chain
    mesh    a ``size`` x ``size`` grid
    grid3d  a ``size``^3 grid: separators of ``size``^2 nodes
    star    ``size`` spokes of 10 segments on one hub: one dense row
    ring    a ring of ``size`` nodes, a chord every 50 nodes to the opposite side
    random  a path of ``size`` nodes and two random edges per node (xorshift64, seed 1)
    tree    a balanced binary tree of depth ``size``

``stages``: ``size`` chains of ``stages`` CMOS inverters between ``vdd`` and ground, the
transistors subcircuits of a model library that ``models`` brings in with the lines of
each dialect. Every chain is driven by the pulse, every second one by its complement, so
that every chain switches and neighbours switch against each other. Without ``wire`` an
inverter drives the next one directly: 2 * ``stages`` * ``size`` transistors in
independent blocks, the device evaluation scaled by their number. With ``wire`` the net
between two inverters is an RC line as a layout extraction writes it: ``ratio`` RC nodes
per transistor (2 * ``ratio`` segments per net) that share the net's resistance ``r`` and
its capacitance to ground ``c``, and a coupling capacitance ``coupling`` to the same net
of the next chain, split over the segments as well. The coupling ties the chains into one
matrix, a grid of ``size`` by 2 * ``ratio`` * ``stages`` nodes whose share of the run
grows with ``ratio``; the totals per net stay, so the waveforms do not depend on it.

The netlists save three node voltages: near the source, inside, far from it. The ngspice
netlist selects KLU (``.options klu``), as the large upstream decks do: ngspice 47
factors with Sparse 1.3 without it.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from .entry import Case, iter_cases

MASK = 2**64 - 1


def _ladder(n):
    return n, [(i, i + 1) for i in range(1, n)], [1, n // 10, n]


def _mesh(m):
    idx = lambda i, j: (i - 1) * m + j
    edges = [(idx(i, j), idx(i + di, j + dj)) for i in range(1, m + 1) for j in range(1, m + 1)
             for di, dj in ((1, 0), (0, 1)) if i + di <= m and j + dj <= m]
    return m * m, edges, [1, idx(m // 2, m // 2), m * m]


def _grid3d(m):
    idx = lambda i, j, k: ((i - 1) * m + (j - 1)) * m + k
    edges = [(idx(i, j, k), idx(i + a, j + b, k + c))
             for i in range(1, m + 1) for j in range(1, m + 1) for k in range(1, m + 1)
             for a, b, c in ((1, 0, 0), (0, 1, 0), (0, 0, 1))
             if i + a <= m and j + b <= m and k + c <= m]
    return m ** 3, edges, [1, idx(m // 2, m // 2, m // 2), m ** 3]


def _star(spokes, segments=10):
    edges, n = [], 1
    for _ in range(spokes):
        prev = 1
        for _ in range(segments):
            n += 1
            edges.append((prev, n))
            prev = n
    return n, edges, [1, segments + 1, n]


def _ring(n, chord=50):
    edges = [(i, i % n + 1) for i in range(1, n + 1)]
    edges += [(i, (i + n // 2 - 1) % n + 1) for i in range(1, n // 2, chord)]
    return n, edges, [1, n // 4, n // 2]


def _random(n, seed=1):
    state = seed | 1

    def draw(k):
        nonlocal state
        state ^= (state << 13) & MASK
        state ^= state >> 7
        state ^= (state << 17) & MASK
        return state % k

    edges = {(i, i + 1) for i in range(1, n)}
    for i in range(1, n + 1):
        for _ in range(2):
            j = draw(n) + 1
            if j != i:
                edges.add((min(i, j), max(i, j)))
    return n, sorted(edges), [1, n // 2, n]


def _tree(depth):
    n = 2 ** depth - 1
    return n, [(i // 2, i) for i in range(2, n + 1)], [1, 2 ** (depth - 1), n]


NETWORKS = {"ladder": _ladder, "mesh": _mesh, "grid3d": _grid3d, "star": _star,
            "ring": _ring, "random": _random, "tree": _tree}
DIODE = "dn"            # the model name of a network's diodes

# An element: (kind, name, nodes, value). ``v``: (DC value, pulse or None); ``r``, ``c``:
# the value; ``d``: None, the model is DIODE; ``x``: (subcircuit, parameters).
Element = tuple[str, str, tuple[str, ...], object]


def _network(g: dict, size: int) -> tuple[str, list[Element], list[str]]:
    n, edges, probes = NETWORKS[g["network"]](size)
    elements: list[Element] = [("v", "vin", ("src", "0"), (g["pulse"]["v1"], g["pulse"])),
                               ("r", "rsrc", ("src", "n1"), g["source_r"])]
    elements += [("c", f"c{i}", (f"n{i}", "0"), g["c"]) for i in range(1, n + 1)]
    elements += [("r", f"r{k}", (f"n{a}", f"n{b}"), g["r"]) for k, (a, b) in enumerate(edges, 1)]
    if "diode" in g:
        elements += [("d", f"d{i}", (f"n{i}", "0"), None) for i in range(1, n + 1)]
    return (f"{n} nodes, {len(edges)} resistors" + (f", {n} diodes" if "diode" in g else ""),
            elements, [f"n{q}" for q in probes])


def _chains(g: dict, size: int) -> tuple[str, list[Element], list[str]]:
    stages, wire, p = g["stages"], g.get("wire"), g["pulse"]
    segments = 2 * wire["ratio"] if wire else 0
    complement = p | {"v1": p["v2"], "v2": p["v1"]}
    elements: list[Element] = [("v", "vdd", ("vdd", "0"), (g["vdd"], None)),
                               ("v", "vin", ("in", "0"), (p["v1"], p)),
                               ("v", "vinb", ("inb", "0"), (complement["v1"], complement))]
    node = lambda k, s, j=0: f"k{k}s{s}" + (f"w{j}" if j else "")
    for k in range(1, size + 1):
        gate = "inb" if k % 2 == 0 else "in"
        for s in range(1, stages + 1):
            out = node(k, s)
            elements += [("x", f"xp{k}_{s}", (out, gate, "vdd", "vdd"), (g["pmos"]["subckt"], g["pmos"])),
                         ("x", f"xn{k}_{s}", (out, gate, "0", "0"), (g["nmos"]["subckt"], g["nmos"]))]
            for j in range(1, segments + 1):
                at = node(k, s, j)
                elements += [("r", f"r{k}_{s}_{j}", (node(k, s, j - 1), at), wire["r"] / segments),
                             ("c", f"c{k}_{s}_{j}", (at, "0"), wire["c"] / segments)]
                if k < size:
                    elements.append(("c", f"cc{k}_{s}_{j}", (at, node(k + 1, s, j)),
                                     wire["coupling"] / segments))
            gate = node(k, s, segments)
    mid = (size + 1) // 2
    probes = [node(1, 1, segments), node(mid, (stages + 1) // 2, segments), node(size, stages, segments)]
    title = f"{size} chains of {stages} inverters, {2 * stages * size} transistors"
    if wire:
        title += f", {segments * stages * size} RC nodes"
    return title, elements, list(dict.fromkeys(probes))


def _num(x: float) -> str:
    return repr(float(x)).replace("e+", "e")


def _params(p: dict) -> str:
    return " ".join(f"{k}={_num(v)}" for k, v in p.items() if k != "subckt")


def _ngspice(g: dict, title: str, elements: list[Element], probes: list[str]) -> list[str]:
    lines = [title, *g.get("models", {}).get("ngspice", [])]
    if "diode" in g:
        lines.append(f".model {DIODE} d {_params(g['diode'])}")
    for kind, name, nodes, value in elements:
        at = " ".join(nodes)
        if kind == "v":
            dc, p = value
            pulse = (f" pulse({_num(p['v1'])} {_num(p['v2'])} {_num(p['delay'])} {_num(p['rise'])} "
                     f"{_num(p['fall'])} {_num(p['width'])} {_num(p['period'])})") if p else ""
            lines.append(f"{name} {at} dc {_num(dc)}{pulse}")
        elif kind in "rc":
            lines.append(f"{name} {at} {_num(value)}")
        elif kind == "d":
            lines.append(f"{name} {at} {DIODE}")
        else:
            lines.append(f"{name} {at} {value[0]} {_params(value[1])}")
    t = g["tran"]
    return lines + [".options klu", ".save " + " ".join(f"v({q})" for q in probes),
                    ".op", f".tran {_num(t['step'])} {_num(t['stop'])}", ".end"]


# VACASK: the OSDI file and the module of an element kind, and the model the elements name.
VACASK_DEVICES = {"r": ("spice/resistor.osdi", "model r sp_resistor"),
                  "c": ("spice/capacitor.osdi", "model c sp_capacitor"),
                  "d": ("spice/diode.osdi", f"model {DIODE} sp_diode")}


def _vacask(g: dict, title: str, elements: list[Element], probes: list[str]) -> list[str]:
    kinds = [k for k in VACASK_DEVICES if any(e[0] == k for e in elements)]
    lines = [title, *g.get("models", {}).get("vacask", [])]
    lines += [f'load "{VACASK_DEVICES[k][0]}"' for k in kinds]
    lines += [VACASK_DEVICES[k][1] for k in kinds if k != "d"] + ["model vsource vsource"]
    if "d" in kinds:
        lines.append(f"{VACASK_DEVICES['d'][1]} {_params(g['diode'])}")
    for kind, name, nodes, value in elements:
        at = f"({' '.join(nodes)})"
        if kind == "v":
            dc, p = value
            pulse = (f' type="pulse" val0={_num(p["v1"])} val1={_num(p["v2"])} '
                     f'delay={_num(p["delay"])} rise={_num(p["rise"])} fall={_num(p["fall"])} '
                     f'width={_num(p["width"])} period={_num(p["period"])}') if p else ""
            lines.append(f"{name} {at} vsource dc={_num(dc)}{pulse}")
        elif kind in "rc":
            lines.append(f"{name} {at} {kind} {kind}={_num(value)}")
        elif kind == "d":
            lines.append(f"{name} {at} {DIODE}")
        else:
            lines.append(f"{name} {at} {value[0]} {_params(value[1])}")
    t = g["tran"]
    return lines + ["control", "  save " + " ".join(f"v({q})" for q in probes),
                    "  analysis op1 op",
                    f"  analysis tran1 tran step={_num(t['step'])} stop={_num(t['stop'])}", "endc"]


WRITERS = {"ngspice": _ngspice, "vacask": _vacask}


def circuit(case: Case, size: int) -> tuple[str, list[Element], list[str]]:
    """A generated case at a size: what its title says of it, its elements, the nodes saved."""
    g = case.raw["generator"]
    return (_network if "network" in g else _chains)(g, size)


def netlist(case: Case, file: str) -> bytes:
    """What the generator writes for a netlist of a generated case."""
    nl = next(n for n in case.raw["netlists"] if n["file"] == file)
    what, elements, probes = circuit(case, nl["size"])
    title = f"{case.title}, size {nl['size']}: {what}"
    return ("\n".join(WRITERS[nl["dialect"]](case.raw["generator"], title, elements, probes)) + "\n").encode()


def generated(case: Case) -> bool:
    return "generator" in case.raw


def write(cases: list[Case] | None = None) -> list[Path]:
    """Write the netlists of generated cases that are missing or differ; the paths written."""
    written = []
    for case in cases if cases is not None else iter_cases():
        if not generated(case):
            continue
        for nl in case.raw["netlists"]:
            path = case.directory / nl["file"]
            data = netlist(case, nl["file"])
            if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != hashlib.sha256(data).hexdigest():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                written.append(path)
    return written
