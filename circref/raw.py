"""SPICE rawfiles, binary and ASCII, real and complex, as ngspice, Xyce and others write
them. Signal names are normalized: lower case, ``v(node)``, ``i(source)``."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Plot:
    name: str                                   # "Transient Analysis", ...
    signals: dict[str, np.ndarray] = field(default_factory=dict)   # the first is the axis


def signal_name(name: str) -> str:
    n = name.strip().lower().replace(":", ".")          # Xyce: x1:n, ngspice: x1.n
    if n.endswith("#branch"):
        return f"i({n[:-7]})"
    if re.fullmatch(r"[vi]\([^()]+\)", n) or n in ("time", "frequency", "sweep"):
        return n.replace(" ", "")
    return f"v({n})"


def read(data: bytes) -> list[Plot]:
    plots: list[Plot] = []
    pos = 0
    while pos < len(data):
        header: dict[str, str] = {}
        names: list[str] = []
        while True:
            end = data.index(b"\n", pos)
            line = data[pos:end].decode("latin-1").rstrip("\r")
            pos = end + 1
            key, _, value = line.partition(":")
            key = key.strip().lower()
            if key == "variables":
                n = int(header["no. variables"])
                for _ in range(n):
                    end = data.index(b"\n", pos)
                    names.append(data[pos:end].decode("latin-1").split()[1])
                    pos = end + 1
            elif key in ("binary", "values"):
                break
            elif key:
                header[key] = value.strip()
        nvar, npts = int(header["no. variables"]), int(header["no. points"])
        complex_ = "complex" in header.get("flags", "").lower()
        width = 2 if complex_ else 1
        if key == "binary":
            count = nvar * npts * width
            values = np.frombuffer(data, "<f8", count, pos)
            pos += 8 * count
        else:
            tokens, need = [], nvar * npts
            while len(tokens) < need and pos < len(data):
                end = data.find(b"\n", pos)
                end = len(data) if end < 0 else end
                line = data[pos:end].decode("latin-1").split()
                pos = end + 1
                if not line:
                    continue
                if len(tokens) % nvar == 0 and len(line) == 2:  # point index, first value
                    line = line[1:]
                tokens += [complex(*map(float, t.split(","))) if complex_ else float(t)
                           for t in line]
            values = np.array(tokens)
        if key == "binary" and complex_:
            values = values[0::2] + 1j * values[1::2]
        table = values.reshape(npts, nvar)
        plot = Plot(header.get("plotname", ""))
        for k, n in enumerate(names):
            plot.signals[signal_name(n)] = table[:, k]
        plots.append(plot)
        while pos < len(data) and data[pos:pos + 1] in (b"\n", b"\r"):
            pos += 1
    return plots

