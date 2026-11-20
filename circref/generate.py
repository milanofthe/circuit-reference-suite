"""Generated cases: circuits written by a generator here instead of taken from upstream.

A generated case states its generator in case.toml (``[generator]``, and ``size`` per
netlist); its netlists are listed under files with provenance ``generated`` and the
sha256 of what the generator writes, so that a change of the generator fails check. They
are not committed (.gitignore): build writes them, and validate, check and run write the
ones that are missing.

``network``: a linear RC network, a capacitor ``c`` from every node to ground and a
resistor ``r`` per edge of a graph, driven at node 1 through ``source_r`` by a source of
the DC value ``dc`` and a pulse in time. The netlists run the operating point, one linear
solve of the resistor network, and the transient. The networks differ only in the graph,
and with it in the elimination structure of the matrix:

    ladder  a path of ``size`` nodes: the elimination tree is one chain
    mesh    a ``size`` x ``size`` grid
    grid3d  a ``size``^3 grid: separators of ``size``^2 nodes
    star    ``size`` spokes of 10 segments on one hub: one dense row
    ring    a ring of ``size`` nodes, a chord every 50 nodes to the opposite side
    random  a path of ``size`` nodes and two random edges per node (xorshift64, seed 1)
    tree    a balanced binary tree of depth ``size``

The netlists save three node voltages: node 1, one inside, one far from the source. The
ngspice netlist selects KLU (``.options klu``), as the large upstream decks do: ngspice 47
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


def _num(x: float) -> str:
    return repr(float(x)).replace("e+", "e")


def _ngspice(g: dict, title: str, n: int, edges, probes) -> list[str]:
    p = g["pulse"]
    lines = [title,
             f"vin src 0 dc {_num(g['dc'])} pulse({_num(p['v1'])} {_num(p['v2'])} {_num(p['delay'])} {_num(p['rise'])} "
             f"{_num(p['fall'])} {_num(p['width'])} {_num(p['period'])})",
             f"rsrc src n1 {_num(g['source_r'])}"]
    lines += [f"c{i} n{i} 0 {_num(g['c'])}" for i in range(1, n + 1)]
    lines += [f"r{k} n{a} n{b} {_num(g['r'])}" for k, (a, b) in enumerate(edges, 1)]
    t = g["tran"]
    return lines + [".options klu", ".save " + " ".join(f"v(n{q})" for q in probes),
                    ".op", f".tran {_num(t['step'])} {_num(t['stop'])}", ".end"]


def _vacask(g: dict, title: str, n: int, edges, probes) -> list[str]:
    p = g["pulse"]
    lines = [title, 'load "spice/resistor.osdi"', 'load "spice/capacitor.osdi"',
             "model r sp_resistor", "model c sp_capacitor", "model vsource vsource",
             f'vin (src 0) vsource dc={_num(g["dc"])} type="pulse" val0={_num(p["v1"])} val1={_num(p["v2"])} '
             f'delay={_num(p["delay"])} rise={_num(p["rise"])} fall={_num(p["fall"])} '
             f'width={_num(p["width"])} period={_num(p["period"])}',
             f"rsrc (src n1) r r={_num(g['source_r'])}"]
    lines += [f"c{i} (n{i} 0) c c={_num(g['c'])}" for i in range(1, n + 1)]
    lines += [f"r{k} (n{a} n{b}) r r={_num(g['r'])}" for k, (a, b) in enumerate(edges, 1)]
    t = g["tran"]
    return lines + ["control", "  save " + " ".join(f"v(n{q})" for q in probes),
                    "  analysis op1 op",
                    f"  analysis tran1 tran step={_num(t['step'])} stop={_num(t['stop'])}", "endc"]


WRITERS = {"ngspice": _ngspice, "vacask": _vacask}


def netlist(case: Case, file: str) -> bytes:
    """What the generator writes for a netlist of a generated case."""
    g = case.raw["generator"]
    nl = next(n for n in case.raw["netlists"] if n["file"] == file)
    n, edges, probes = NETWORKS[g["network"]](nl["size"])
    title = f"{case.title}, size {nl['size']}: {n} nodes, {len(edges)} resistors"
    return ("\n".join(WRITERS[nl["dialect"]](g, title, n, edges, probes)) + "\n").encode()


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
