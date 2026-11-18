"""One adapter per simulator: the circuit body it reads as written, and the lines that
state a circuit's options, one analysis and its outputs in the simulator's dialect.

An adapter writes one deck per analysis, so that every simulator runs the same unit and
every analysis gets a time of its own; the run writes a rawfile the reader in raw.py
turns into signals.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from .circuit import Circuit
from .entry import ROOT

# Lines of a deck that state what to compute rather than the circuit. With their
# continuation lines, and every control block, they are not part of the body.
NOT_BODY = {"op", "tran", "ac", "dc", "noise", "tf", "pz", "sens", "disto", "four", "hb",
            "print", "plot", "probe", "save", "width", "meas", "measure", "step", "sampling",
            "option", "options", "opt", "opts", "temp", "end", "control", "endc", "lin"}


def body(text: str) -> list[str]:
    """The circuit of a SPICE deck: its lines without analysis, output, option and
    control lines. The title line stays first."""
    lines = text.splitlines()
    out = lines[:1]
    skip = control = False
    for line in lines[1:]:
        s = line.strip().lower()
        if control:
            control = s != ".endc"
            continue
        if s.startswith("+"):
            if not skip:
                out.append(line)
            continue
        head = s.split()[0][1:] if s.startswith(".") and len(s) > 1 else ""
        control = head == "control"
        skip = control or head in NOT_BODY
        if not skip:
            out.append(line)
    return out


def _num(x: float) -> str:
    return repr(float(x)).replace("e+", "e")


@dataclass(frozen=True)
class Adapter:
    name: str
    dialects: tuple[str, ...]           # bodies read as written
    osdi: bool = False                  # loads Verilog-A compiled to OSDI
    timing: str | None = None           # the simulator's own analysis time, seconds

    def version(self) -> str:
        f = Path(os.environ.get("SIMS", "/cache/circsims")) / self.name / "current" / "version"
        return f.read_text().strip() if f.exists() else ""

    def analysis(self, a: dict) -> str:
        t = a["type"]
        if t == "op":
            return ".op"
        if t == "dc":
            return ".dc " + " ".join(f"{s['source']} {_num(s['start'])} {_num(s['stop'])} "
                                     f"{_num(s['step'])}" for s in a["sweep"])
        if t == "ac":
            return f".ac {a['sweep']} {a['points']} {_num(a['start'])} {_num(a['stop'])}"
        line = f".tran {_num(a['step'])} {_num(a['stop'])}"
        if "start" in a or "max_step" in a:
            line += f" {_num(a.get('start', 0))}"
        if "max_step" in a:
            line += f" {_num(a['max_step'])}"
        return line + (" uic" if a.get("uic") else "")

    def control(self, circuit: Circuit) -> list[str]:
        """Options and outputs."""
        raise NotImplementedError

    def preload(self, directory: Path, osdi: list[Path]) -> None:
        if osdi:
            raise NotImplementedError(f"{self.name}: Verilog-A types without a load")

    def argv(self, deck: str, raw: str) -> list[str]:
        raise NotImplementedError

    def deck(self, circuit: Circuit, text: str, analysis: dict) -> str:
        return "\n".join(body(text) + self.control(circuit) + [self.analysis(analysis), ".end", ""])


class Ngspice(Adapter):
    def control(self, c: Circuit) -> list[str]:
        opts = [f"{k}={v if k == 'method' else _num(v)}" for k, v in c.options.items()]
        lines = [".options acct " + " ".join(opts)]
        if c.outputs:
            lines.append(".save " + " ".join(c.outputs))
        return lines

    def preload(self, directory: Path, osdi: list[Path]) -> None:
        if osdi:
            init = directory / ".spiceinit"
            old = init.read_text() if init.exists() else ""
            init.write_text(old + "".join(f"osdi {p}\n" for p in osdi))

    def argv(self, deck: str, raw: str) -> list[str]:
        return ["ngspice", "-b", "-r", raw, deck]


class Xyce(Adapter):
    GROUPS = {"temp": "device", "tnom": "device", "gmin": "device", "reltol": "timeint",
              "abstol": "timeint", "method": "timeint"}

    def control(self, c: Circuit) -> list[str]:
        groups: dict[str, list[str]] = {}
        for k, v in c.options.items():
            if k in self.GROUPS:
                groups.setdefault(self.GROUPS[k], []).append(f"{k}={v if k == 'method' else _num(v)}")
        return [f".options {g} " + " ".join(kv) for g, kv in groups.items()]

    def argv(self, deck: str, raw: str) -> list[str]:
        return ["Xyce", "-r", raw, deck]


class Sane(Ngspice):
    """SANE reads the ngspice deck's body; sims/sane/run.py the rest."""

    def preload(self, directory: Path, osdi: list[Path]) -> None:
        Adapter.preload(self, directory, osdi)

    def argv(self, deck: str, raw: str) -> list[str]:
        return [sys.executable, str(ROOT / "sims" / "sane" / "run.py"), deck, raw]


ADAPTERS = {a.name: a for a in (
    Ngspice("ngspice", ("ngspice", "spice3"), osdi=True,
            timing=r"Total analysis time \(seconds\)\s*=\s*([\d.eE+-]+)"),
    Xyce("xyce", ("xyce",), timing=r"Total Simulation Solvers Run Time:\s*([\d.eE+-]+)"),
    Sane("sane", ("ngspice", "spice3"), timing=r"Total analysis time \(seconds\)\s*=\s*([\d.eE+-]+)"),
)}
