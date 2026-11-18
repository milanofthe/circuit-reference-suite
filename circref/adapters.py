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

from .circuit import OPTIONS, Circuit
from .entry import ROOT

# Lines of a deck that state what to compute rather than the circuit. With their
# continuation lines, and every control block, they are not part of the body.
NOT_BODY = {"op", "tran", "ac", "dc", "noise", "tf", "pz", "sens", "disto", "four", "hb",
            "print", "plot", "probe", "save", "width", "meas", "measure", "step", "sampling",
            "temp", "end", "control", "endc", "lin"}
OPTION_LINES = {"option", "options", "opt", "opts"}
# An option the circuit states itself; every other option stays with the body, since
# it can change what the circuit means (Xyce's model_binning, ngspice's scale).
_MANAGED = re.compile(r"\b(?:" + "|".join(OPTIONS) + r")\s*=\s*[^\s,]+", re.I)


def _statements(lines: list[str]):
    """(first line, continuation lines) per statement; comment and blank lines between a
    statement and its continuation belong to neither and come out on their own."""
    current: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("+") and current:
            current.append(line)
            continue
        if not s or s[0] in "*;":
            if current:
                current.append(line)                    # kept in order, judged with it
            else:
                yield [line]
            continue
        if current:
            yield current
        current = [line]
    if current:
        yield current


def body(text: str) -> list[str]:
    """The circuit of a SPICE deck: its lines without analysis, output and control lines,
    and without the options the circuit states itself. The title line stays first."""
    lines = text.splitlines()
    out = lines[:1]
    control = False
    for st in _statements(lines[1:]):
        s = st[0].strip().lower()
        if control:
            control = not any(l.strip().lower().startswith(".endc") for l in st)
            continue
        head = s.split()[0][1:] if s.startswith(".") and len(s) > 1 else ""
        if head == "control":
            control = not any(l.strip().lower().startswith(".endc") for l in st[1:])
            continue
        if head in NOT_BODY:
            continue
        if head in OPTION_LINES:
            st = [_MANAGED.sub("", l) for l in st]
            words = " ".join(l.strip().lstrip("+") for l in st if l.strip()[:1] not in "*;").split()[1:]
            if not [w for w in words if w.lower() not in ("device", "timeint", "nonlin", "parser")
                    or "=" in w]:
                continue
        out += st
    return out


def _num(x: float) -> str:
    return repr(float(x)).replace("e+", "e")


@dataclass(frozen=True)
class Adapter:
    name: str
    dialects: tuple[str, ...]           # bodies read as written
    osdi: bool = False                  # loads Verilog-A compiled to OSDI
    timing: str | None = None           # the simulator's own analysis time, seconds
    error: str | None = None            # a line that marks a failed run despite exit 0

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
    # ngspice's step bound when tstep does not set one: (tstop - tstart) / 50 (traninit.c).
    STEPS = 50
    # Devices with a branch current, the currents ngspice saves and reads in expressions.
    BRANCH = ("v", "e", "h", "l")

    def analysis(self, a: dict) -> str:
        """ngspice needs tstep > 0; without one the bound it uses by itself."""
        if a["type"] == "tran" and not a["step"]:
            a = a | {"step": (a["stop"] - a.get("start", 0)) / self.STEPS}
        return super().analysis(a)

    def control(self, c: Circuit) -> list[str]:
        opts = [f"{k}={v if k == 'method' else _num(v)}" for k, v in c.options.items()]
        lines = [".options acct " + " ".join(opts)]
        # .save takes the currents of devices with a branch only; any other i(x) (a lead
        # current, as in Xyce) ends the run with "no data saved".
        saved = [s for s in c.outputs if s[:2] == "v(" or
                 s[2:3].lower() in self.BRANCH and ":" not in s]
        if saved:
            lines.append(".save " + " ".join(saved))
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
            timing=r"Total analysis time \(seconds\)\s*=\s*([\d.eE+-]+)",
            error=r"^Error\b.*|^.*Simulation interrupted.*|^.*no simulations run.*"),
    Xyce("xyce", ("xyce",), timing=r"Total Simulation Solvers Run Time:\s*([\d.eE+-]+)"),
    Sane("sane", ("ngspice", "spice3"), timing=r"Total analysis time \(seconds\)\s*=\s*([\d.eE+-]+)"),
)}
