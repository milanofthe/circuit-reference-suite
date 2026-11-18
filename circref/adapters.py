"""One adapter per simulator: the circuit body it reads as written, and the lines that
state a circuit's options, one analysis and its outputs in the simulator's dialect.

An adapter writes one deck per analysis, so that every simulator runs the same unit and
every analysis gets a time of its own; the run writes a rawfile the reader in raw.py
turns into signals.
"""
from __future__ import annotations

import math
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import raw as rawfile
from .circuit import OPTIONS, Circuit, number, vacask_split
from .entry import ROOT

# Lines of a deck that state what to compute rather than the circuit. With their
# continuation lines, and every control block, they are not part of the body.
NOT_BODY = {"op", "tran", "ac", "dc", "noise", "tf", "pz", "sens", "disto", "four", "hb",
            "print", "plot", "probe", "save", "width", "meas", "measure", "step", "sampling",
            "temp", "end", "control", "endc", "lin",
            # gnucap commands that report rather than define
            "list", "status", "stat", "tr", "portdump", "fanout", "alarm", "mark", "unmark"}
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

    def deck(self, circuit: Circuit, text: str, analysis: dict, raw: str) -> str:
        return "\n".join(body(text) + self.control(circuit) + [self.analysis(analysis), ".end", ""])

    def read(self, path: Path, analysis: dict) -> dict[str, np.ndarray]:
        """The signals the run wrote to ``path``; the first is the axis."""
        return rawfile.read(path.read_bytes())[-1].signals


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


class Gnucap(Adapter):
    """gnucap prints tables: ``.print`` names the columns, the analysis redirects them into
    the file the run reads (``> file``); the first column is the axis, at op the
    temperature."""

    def deck(self, c: Circuit, text: str, a: dict, raw: str) -> str:
        opts = " ".join(f"{k}={v if k == 'method' else _num(v)}" for k, v in c.options.items())
        t = a["type"]
        signals = c.outputs or ["v(nodes)"]
        if t == "ac":                                   # complex: real and imaginary parts
            signals = [f"{s[0]}{part}{s[1:]}" for s in signals for part in "ri"]
        if t == "op":
            line = ".op"
        elif t == "dc":
            if len(a["sweep"]) != 1:
                raise NotImplementedError("gnucap: nested dc sweeps")
            sw = a["sweep"][0]
            line = f".dc {sw['source']} {_num(sw['start'])} {_num(sw['stop'])} {_num(sw['step'])}"
        elif t == "ac":
            step = (f"{_num((a['stop'] - a['start']) / max(a['points'] - 1, 1))}" if a["sweep"] == "lin"
                    else f"{a['sweep']} {a['points']}")
            line = f".ac {_num(a['start'])} {_num(a['stop'])} {step}"
        else:
            line = f".tran {_num(a.get('start', 0))} {_num(a['stop'])} {_num(a['step'])}"
            if a.get("uic"):
                line += " uic"
        return "\n".join(body(text) + [f".options numdgt=12 {opts}", ".width out=100000",
                                        f".print {t} " + " ".join(signals), f"{line} > {raw}",
                                        ".end", ""])

    def read(self, path: Path, analysis: dict) -> dict[str, np.ndarray]:
        lines = [l.split() for l in path.read_text(encoding="latin-1").splitlines() if l.strip()]
        head = next(i for i, l in enumerate(lines) if l[0].startswith("#"))
        names = [lines[head][0][1:] or "axis"] + lines[head][1:]
        table = np.array([[number(x) for x in l] for l in lines[head + 1:]])
        cols = {n.lower(): table[:, k] for k, n in enumerate(names)}
        out: dict[str, np.ndarray] = {}
        for n, col in cols.items():
            m = re.fullmatch(r"([vi])([ri])\((.+)\)", n)
            if m and m[2] == "r":
                out[f"{m[1]}({m[3]})"] = col + 1j * cols.get(f"{m[1]}i({m[3]})", 0)
            elif not m:
                out[{"time": "time", "freq": "frequency"}.get(n, n)] = col
        return out

    def argv(self, deck: str, raw: str) -> list[str]:
        return ["gnucap", "--acs", "-b", deck]


class Sane(Ngspice):
    """SANE reads the ngspice deck's body; sims/sane/run.py the rest."""

    def preload(self, directory: Path, osdi: list[Path]) -> None:
        Adapter.preload(self, directory, osdi)

    def argv(self, deck: str, raw: str) -> list[str]:
        return [sys.executable, str(ROOT / "sims" / "sane" / "run.py"), deck, raw]


def total_points(a: dict) -> tuple[int, float]:
    """An ac sweep by its total number of points, both ends included, for simulators that
    state it so; a dec or oct sweep ends on its last point at or below ``stop``."""
    if a["sweep"] == "lin":
        return a["points"], a["stop"]
    base = 10.0 if a["sweep"] == "dec" else 2.0
    n = math.floor(a["points"] * math.log(a["stop"] / a["start"]) / math.log(base) + 1e-9) + 1
    return n, a["start"] * base ** ((n - 1) / a["points"])


def _drop(lines: list[str], heads: set[str]) -> list[str]:
    """Lines without the dot statements in ``heads``."""
    return [l for l in lines if not (l.strip()[:1] == "." and
                                     " ".join(l.strip()[1:].split()[:1]).lower() in heads)]


def _top_nodes(lines: list[str]) -> list[str]:
    """The nodes of the top-level elements of a SPICE-like body: the two after the name
    (all but the last word of a subcircuit call); ground left out."""
    nodes: list[str] = []
    depth = 0
    for line in lines[1:]:
        words = line.split()
        if not words or words[0][0] in "*+#":
            continue
        head = words[0].lower()
        depth += head == ".subckt"
        depth -= head == ".ends"
        if depth or head[0] == ".":
            continue
        args = [w for w in words[1:] if "=" not in w]
        for n in (args[:-1] if head[0] == "x" else args[:2]):
            if n.lower() not in ("0", "gnd") and n.lower() not in nodes:
                nodes.append(n.lower())
    return nodes


class Wrspice(Ngspice):
    """WRspice reads a SPICE3 deck as ngspice does and writes a SPICE3 rawfile."""

    def control(self, c: Circuit) -> list[str]:
        opts = [f"{k}={v if k == 'method' else _num(v)}" for k, v in c.options.items()]
        lines = [".options " + " ".join(opts)] if opts else []
        if c.outputs:
            lines.append(".save " + " ".join(c.outputs))
        return lines

    def preload(self, directory: Path, osdi: list[Path]) -> None:
        Adapter.preload(self, directory, osdi)

    def argv(self, deck: str, raw: str) -> list[str]:
        return ["wrspice", "-b", "-r", raw, deck]


class Josim(Adapter):
    """JoSIM: transient only, from zero initial conditions with a fixed step; ``.print``
    names what it writes into the rawfile."""

    def deck(self, c: Circuit, text: str, a: dict, raw: str) -> str:
        if a["type"] != "tran":
            raise NotImplementedError(f"josim: {a['type']} analysis")
        lines = _drop(body(text), {"iv"})
        line = f".tran {_num(a['step'])} {_num(a['stop'])}"
        if a.get("start"):
            line += f" {_num(a['start'])} {_num(a['step'])}"
        outputs = c.outputs or [f"v({n})" for n in _top_nodes(lines)]
        return "\n".join(lines + [line] + [f".print {s}" for s in outputs] + [".end", ""])

    def argv(self, deck: str, raw: str) -> list[str]:
        return ["josim-cli", "-o", raw, deck]

    def read(self, path: Path, analysis: dict) -> dict[str, np.ndarray]:
        signals = Adapter.read(self, path, analysis)
        return {re.sub(r"^v\(([^,]+),0\)$", r"v(\1)", n): v for n, v in signals.items()}


class Vacask(Adapter):
    """VACASK: the deck without its control block and embedded files; a control block of
    its own keeps the deck's ``elaborate`` lines. The analysis writes ``circref.raw``,
    which the run renames; postprocessing and embedded files are skipped."""

    OPTION_NAMES = {"method": "tran_method"}
    METHODS = {"trap": "trap", "gear": "gear2"}

    def deck(self, c: Circuit, text: str, a: dict, raw: str) -> str:
        outside, inside = vacask_split(text)
        control = [l for l in inside if l.split()[:1] == ["elaborate"]]
        opts = []
        for k, v in c.options.items():
            if k == "method":
                opts.append(f'tran_method="{self.METHODS.get(v, v)}"')
            else:
                opts.append(f"{k}={_num(v)}")
        if opts:
            control.append("options " + " ".join(opts))
        t = a["type"]
        if t == "op":
            control.append("analysis circref op")
        elif t == "dc":
            for k, s in enumerate(reversed(a["sweep"])):          # the last sweep is inner
                control.append(f'sweep s{k} instance="{s["source"]}" parameter="dc" '
                               f'from={_num(s["start"])} to={_num(s["stop"])} step={_num(s["step"])}')
            control.append("analysis circref op")
        elif t == "ac":
            points = a["points"] - 1 if a["sweep"] == "lin" else a["points"]
            control.append(f'analysis circref ac from={_num(a["start"])} to={_num(a["stop"])} '
                           f'mode="{a["sweep"]}" points={points}')
        else:
            line = f"analysis circref tran step={_num(a['step'])} stop={_num(a['stop'])}"
            if a.get("start"):
                line += f" start={_num(a['start'])}"
            if a.get("max_step"):
                line += f" maxstep={_num(a['max_step'])}"
            control.append(line + (' icmode="uic"' if a.get("uic") else ""))
        control.append("print stats")
        return "\n".join(outside + ["control"] + [f"  {l.strip()}" for l in control] + ["endc", ""])

    def argv(self, deck: str, raw: str) -> list[str]:
        return ["sh", "-c", f'vacask -sp -se -qp "$1" && mv circref.raw "$2"', "vacask", deck, raw]

    def read(self, path: Path, analysis: dict) -> dict[str, np.ndarray]:
        signals = Adapter.read(self, path, analysis)
        return {re.sub(r"^v\((.+)\.flow\(br\)\)$", r"i(\1)", n): v for n, v in signals.items()}


class Qucsator(Adapter):
    """qucsator: the netlist without its analysis lines; a dc sweep sweeps the value of the
    source, made a variable; the dataset holds every node voltage and probe current."""

    METHODS = {"trap": "Trapezoidal", "gear": "Gear"}

    def deck(self, c: Circuit, text: str, a: dict, raw: str) -> str:
        lines = [l for l in text.splitlines() if not l.strip().startswith(".")]
        o = c.options
        opts = "".join(f' {q}="{_num(o[k])}"' for k, q in (("temp", "Temp"), ("reltol", "reltol"),
                                                           ("abstol", "abstol"), ("vntol", "vntol"))
                       if k in o)
        t = a["type"]
        if t in ("op", "dc"):
            lines.append(f".DC:DC1{opts}")
            sim = "DC1"
            for k, s in enumerate(a.get("sweep", [])):              # the first sweep is inner
                var = f"circref_{s['source']}"
                pattern = re.compile(rf'^(\s*[VI]dc:{re.escape(s["source"])}\s.*?\b[UI]=)"[^"]*"', re.I)
                hit = [i for i, l in enumerate(lines) if pattern.match(l)]
                if not hit:
                    raise NotImplementedError(f"qucsator: no dc source {s['source']}")
                lines[hit[0]] = pattern.sub(rf'\1"{var}"', lines[hit[0]])
                points = round((s["stop"] - s["start"]) / s["step"]) + 1
                lines.append(f'.SW:SW{k + 1} Sim="{sim}" Type="lin" Param="{var}" '
                             f'Start="{_num(s["start"])}" Stop="{_num(s["stop"])}" Points="{points}"')
                sim = f"SW{k + 1}"
        elif t == "ac":
            n, stop = total_points(a)
            kind = "lin" if a["sweep"] == "lin" else "log"
            lines.append(f'.AC:AC1 Type="{kind}" Start="{_num(a["start"])}" Stop="{_num(stop)}" '
                         f'Points="{n}" Noise="no"')
        else:
            start = a.get("start", 0.0)
            n = round((a["stop"] - start) / a["step"]) + 1
            line = (f'.TR:TR1 Type="lin" Start="{_num(start)}" Stop="{_num(a["stop"])}" Points="{n}"'
                    f'{opts}')
            if o.get("method") in self.METHODS:
                line += f' IntegrationMethod="{self.METHODS[o["method"]]}"'
            if a.get("max_step"):
                line += f' MaxStep="{_num(a["max_step"])}"'
            lines.append(line + (' initialDC="no"' if a.get("uic") else ""))
        return "\n".join(lines + [""])

    def argv(self, deck: str, raw: str) -> list[str]:
        return ["qucsator_rf", "-i", deck, "-o", raw]

    def read(self, path: Path, analysis: dict) -> dict[str, np.ndarray]:
        """The dataset: ``<indep name n>`` and ``<dep name indep...>`` blocks of one value
        per line, complex as ``+1e0-j2e0``; ``n.V``/``n.Vt``/``n.v`` is a node voltage,
        ``x.I``/``x.It``/``x.i`` the current of a probe or source."""
        blocks: dict[str, np.ndarray] = {}
        axis = None
        for kind, name, values in re.findall(r"<(indep|dep) (\S+)[^>]*>\n(.*?)</(?:indep|dep)>",
                                             path.read_text(encoding="latin-1"), re.S):
            data = np.array([complex(v.replace("j", "") + "j") if "j" in v else float(v)
                             for v in values.split()])
            if kind == "indep" and len(data) > 1 and axis is None:
                axis = name
            blocks[name] = data
        out: dict[str, np.ndarray] = {}
        if axis:
            out[{"time": "time", "acfrequency": "frequency"}.get(axis, "sweep")] = blocks[axis]
        for name, data in blocks.items():
            m = re.fullmatch(r"(.+)\.(V|Vt|v|I|It|i)", name)
            if m:
                out[f"{m[2][0].lower()}({m[1].lower()})"] = data
        return out


class Ahkab(Adapter):
    """ahkab: ``-o prefix`` writes ``prefix.<analysis>``, a tab separated table whose
    header names node voltages ``V<node>`` and currents ``I(<source>)``, for ac as
    magnitude ``|x|`` and phase ``arg(x)``; the first column is the axis except at op."""

    NOT_BODY = {"op", "dc", "ac", "tran", "pz", "pss", "symbolic", "plot", "four", "fft",
                "shooting", "end"}

    def deck(self, c: Circuit, text: str, a: dict, raw: str) -> str:
        t = a["type"]
        if t == "op":
            line = ".op"
        elif t == "dc":
            if len(a["sweep"]) != 1:
                raise NotImplementedError("ahkab: nested dc sweeps")
            s = a["sweep"][0]
            line = (f".dc source={s['source']} start={_num(s['start'])} stop={_num(s['stop'])} "
                    f"step={_num(s['step'])}")
        elif t == "ac":
            n, stop = total_points(a)
            line = (f".ac start={_num(a['start'])} stop={_num(stop)} nsteps={n} "
                    f"type={'lin' if a['sweep'] == 'lin' else 'log'}")
        else:
            lines = body(text)
            # zero initial state, or the elements' initial conditions over the operating point
            uic = (2 if any("ic=" in l.lower() for l in lines[1:]) else 0) if a.get("uic") else 1
            line = f".tran tstep={_num(a['step'])} tstop={_num(a['stop'])} uic={uic}"
            if a.get("start"):
                line += f" tstart={_num(a['start'])}"
            method = {"trap": "trap", "gear": "gear2"}.get(c.options.get("method", ""))
            if method:
                line += f" method={method}"
            if uic:                                     # from the .op the run computes first
                line = ".op\n" + line
        return "\n".join(_drop(body(text), self.NOT_BODY) + [line, ".end", ""])

    def argv(self, deck: str, raw: str) -> list[str]:
        prefix = raw.removesuffix(".raw")
        return ["sh", "-c", 'ahkab -o "$1" "$2" || exit; for e in tran ac dc op; do '
                '[ -f "$1.$e" ] && exec mv "$1.$e" "$3"; done; exit 1', "ahkab", prefix, deck, raw]

    def read(self, path: Path, analysis: dict) -> dict[str, np.ndarray]:
        text = path.read_text(encoding="latin-1").splitlines()
        names = [n.strip().lower() for n in text[0].lstrip("#").split("\t")]
        table = np.loadtxt(text[1:], delimiter="\t", ndmin=2)
        out: dict[str, np.ndarray] = {}
        first = 0 if analysis["type"] == "op" else 1
        if first:                                       # the dc axis is named as a node
            out[{"t": "time", "f": "frequency"}.get(names[0], "sweep")] = table[:, 0]
        cols = {n: table[:, k] for k, n in enumerate(names) if k >= first}
        for n, col in cols.items():
            if n.startswith("arg("):
                continue
            if n.startswith("|") and n.endswith("|"):
                n, col = n[1:-1], col * np.exp(1j * cols.get(f"arg({n[1:-1]})", 0))
            out[f"i({n[2:-1]})" if n.startswith("i(") else f"v({n[1:]})"] = col
        return out


ADAPTERS = {a.name: a for a in (
    Ngspice("ngspice", ("ngspice", "spice3"), osdi=True,
            timing=r"Total analysis time \(seconds\)\s*=\s*([\d.eE+-]+)",
            error=r"^Error\b.*|^.*Simulation interrupted.*|^.*no simulations run.*"),
    Xyce("xyce", ("xyce",), timing=r"Total Simulation Solvers Run Time:\s*([\d.eE+-]+)"),
    Gnucap("gnucap", ("gnucap",), error=r"^\s*\^ ?.*|.*can't find.*|.*bad file.*"),
    Sane("sane", ("ngspice", "spice3"), timing=r"Total analysis time \(seconds\)\s*=\s*([\d.eE+-]+)"),
    Wrspice("wrspice", ("wrspice", "spice3"), error=r"^.*Simulation aborted.*|^Error\b.*"),
    Josim("josim", ("josim",)),
    Vacask("vacask", ("vacask",), osdi=True),
    Qucsator("qucsator", ("qucsator",)),
    Ahkab("ahkab", ("ahkab",), error=r"^E: .*|^Traceback.*"),
)}
