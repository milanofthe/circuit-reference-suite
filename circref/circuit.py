"""Benchmark circuits: the simulator-independent interface to the corpus.

A circuit is ``circuits/<name>.toml``. Its body comes from a netlist of a case (``source``),
or from an upstream variant for a dialect where one exists (``variants``); analysis,
output and option lines of those netlists are not used. What every simulator computes is
stated here: the analyses with their parameters, the signals, the options. An adapter
writes them in its simulator's dialect.

    title = "Bipolar ring oscillator"
    case = "vacask_bjtring"
    source = "ngspice/runme.sim"
    outputs = ["v(9)", "i(vcc)"]           # empty: every node voltage

    [variants]
    xyce = "xyce/runme.sim"

    [options]
    temp = 27.0

    [[analysis]]
    type = "tran"
    step = 1e-9
    stop = 1e-6
"""
from __future__ import annotations

import math
import re
import tomllib
from dataclasses import dataclass
from decimal import Decimal
from functools import cached_property
from pathlib import Path

import tomli_w

from . import classify
from .entry import ROOT, Case, Netlist, iter_cases, load_case, validate_schema

CIRCUIT_DIR = ROOT / "circuits"

# Dialects whose analysis lines follow SPICE's argument order.
SPICE_ORDER = ("ngspice", "spice3", "xyce", "hspice", "pspice", "tspice", "spicesharp", "wrspice")
# The source of a circuit with variants in several dialects: the first of these present.
SOURCE_PREFERENCE = SPICE_ORDER + ("gnucap", "vacask", "spectre", "qucsator", "ahkab", "josim",
                                   "cedarsim")
# Options every adapter knows how to state.
OPTIONS = ("temp", "tnom", "reltol", "abstol", "vntol", "chgtol", "gmin", "method")


@dataclass(frozen=True)
class Circuit:
    path: Path
    raw: dict

    @property
    def name(self) -> str:
        return self.path.stem

    @cached_property
    def case(self) -> Case:
        return load_case(self.raw["case"])

    @property
    def source(self) -> Netlist:
        return self.netlist(self.raw["source"])

    def netlist(self, file: str) -> Netlist:
        return next(n for n in self.case.netlists() if n.file == file)

    @property
    def variants(self) -> dict[str, Netlist]:
        return {d: self.netlist(f) for d, f in self.raw.get("variants", {}).items()}

    @property
    def analyses(self) -> list[dict]:
        return self.raw["analysis"]

    @property
    def outputs(self) -> list[str]:
        return self.raw.get("outputs", [])

    @property
    def options(self) -> dict:
        return self.raw.get("options", {})

    def errors(self) -> list[str]:
        errors = validate_schema(self.raw, "circuit")
        if errors:
            return errors
        files = {n.file: n for n in self.case.netlists()}
        for dialect, f in [(None, self.raw["source"]), *self.raw.get("variants", {}).items()]:
            if f not in files:
                errors.append(f"{f}: not a netlist of case {self.raw['case']}")
            elif dialect and files[f].dialect != dialect:
                errors.append(f"variant {dialect}: {f} is {files[f].dialect}")
        return errors


def load_circuit(ref: str | Path) -> Circuit:
    path = Path(ref) if str(ref).endswith(".toml") else CIRCUIT_DIR / f"{ref}.toml"
    return Circuit(path, tomllib.loads(path.read_text(encoding="utf-8")))


def iter_circuits() -> list[Circuit]:
    return [load_circuit(p) for p in sorted(CIRCUIT_DIR.glob("*.toml"))]


# --------------------------------------------------------------- from the decks

class Unsupported(Exception):
    pass


_EXPONENT = {"t": 12, "g": 9, "meg": 6, "k": 3, "m": -3, "u": -6, "n": -9, "p": -12, "f": -15}
_NUMBER = re.compile(r"([-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?)(meg|mil|[tgkmunpf])?[a-z]*$", re.I)


def number(token: str) -> float:
    """A SPICE number: ``1.5u``, ``10meg``, ``2ns``. An expression is not a number."""
    m = _NUMBER.match(token.strip())
    if not m:
        raise Unsupported(f"not a number: {token!r}")
    suffix = (m.group(2) or "").lower()
    if suffix == "mil":
        return float(m.group(1)) * 25.4e-6
    return float(Decimal(m.group(1)).scaleb(_EXPONENT.get(suffix, 0)))     # 50p: 5e-11 exactly


def lines(text: str) -> list[str]:
    """Logical lines: continuations joined, comments dropped, lower case."""
    out: list[str] = []
    for raw in text.splitlines()[1:]:                       # the first line is the title
        line = re.split(r"\s;|^;|\s\$\s|\s\$$|\s//", raw.strip(), maxsplit=1)[0].rstrip()
        if not line or line[0] in "*'":
            continue
        if line[0] == "+" and out:
            out[-1] += " " + line[1:].strip()
        else:
            out.append(line)
    return [re.sub(r"\s*=\s*", "=", l.lower()) for l in out]


_SIGNAL = re.compile(r"\b([vi])(?:[rimpdb]{0,2})\(\s*([^(),\s]+)\s*(?:,\s*([^(),\s]+)\s*)?\)")


def _signals(tokens: str) -> list[str]:
    """``v(a)``, ``v(a,b)``, ``i(vx)`` from a print line; magnitude, phase and dB forms of
    the same signal are one signal, expressions are dropped."""
    out = []
    for kind, a, b in _SIGNAL.findall(re.sub(r"\{[^}]*\}", "", tokens)):
        if a in ("nodes", "all", "*") or "*" in a or "?" in a:     # wildcards
            continue
        s = f"{kind}({a},{b})" if b and b != "0" else f"{kind}({a})"
        if s not in out:
            out.append(s)
    return out


def spice_analysis(head: str, args: list[str]) -> dict:
    flags = [a for a in args if "=" not in a]
    if head == "op":
        return {"type": "op"}
    if head == "tran":
        nums = [a for a in flags if a != "uic"]
        if len(nums) < 2:
            raise Unsupported(".tran without step and stop")
        a = {"type": "tran", "step": number(nums[0]), "stop": number(nums[1])}
        if len(nums) > 2 and number(nums[2]):
            a["start"] = number(nums[2])
        if len(nums) > 3:
            a["max_step"] = number(nums[3])
        if "uic" in flags:
            a["uic"] = True
        return a
    if head == "ac":
        if len(flags) != 4 or flags[0] not in ("dec", "oct", "lin"):
            raise Unsupported(f".ac {' '.join(args)}")
        return {"type": "ac", "sweep": flags[0], "points": int(number(flags[1])),
                "start": number(flags[2]), "stop": number(flags[3])}
    if head == "dc":
        flags = [f for f in flags if f != "lin"]
        if len(flags) not in (4, 8) or any(f in ("dec", "oct", "list", "data") for f in flags):
            raise Unsupported(f".dc {' '.join(args)}")
        sweeps = [{"source": flags[i], "start": number(flags[i + 1]), "stop": number(flags[i + 2]),
                   "step": number(flags[i + 3])} for i in range(0, len(flags), 4)]
        return {"type": "dc", "sweep": sweeps}
    raise Unsupported(f".{head}")


def _gnucap_analysis(head: str, args: list[str]) -> dict:
    """gnucap's order: ``tran start stop step``, ``ac start stop {step | dec n | oct n}``;
    words after the numbers (``trace all``) only change what is printed."""
    nums, words = [], []
    for a in args:
        try:
            nums.append(number(a)) if not words else words.append(a)
        except Unsupported:
            words.append(a)
    if head == "op":
        if nums:
            raise Unsupported(".op over a temperature or sweep")
        return {"type": "op"}
    if head in ("tran", "tr"):
        if len(nums) != 3:
            raise Unsupported(f".tran {' '.join(args)}")
        a = {"type": "tran", "step": nums[2], "stop": nums[1]}
        if nums[0]:
            a["start"] = nums[0]
        return a
    if head == "ac":
        if len(nums) == 3:
            points = round((nums[1] - nums[0]) / nums[2]) + 1
            return {"type": "ac", "sweep": "lin", "points": points, "start": nums[0], "stop": nums[1]}
        if len(nums) == 2 and len(words) >= 2 and words[0] in ("dec", "oct"):
            return {"type": "ac", "sweep": words[0], "points": int(number(words[1])),
                    "start": nums[0], "stop": nums[1]}
        raise Unsupported(f".ac {' '.join(args)}")
    if head == "dc":
        return spice_analysis("dc", args)
    raise Unsupported(f".{head}")


# A gnucap deck that changes its circuit between analyses is a script, not a circuit.
_GNUCAP_SCRIPTED = {"modify", "delete", "alter", "gen", "generator", "measure", "exp", "load",
                    "fanout", "alarm", "mark", "unmark", "store"}
# gnucap prints several nodes in one probe: v(1 2 3).
_MULTI = re.compile(r"\b([vi])(?:[rimpdb]{0,2})\(([^(),]+\s[^(),]+)\)")

# A control script that changes the circuit between analyses states more than analyses.
_SCRIPTED = {"alter", "altermod", "foreach", "repeat", "while", "dowhile", "if", "reset",
             "source", "set appendwrite", "mc_source"}
# What keeps a netlist from being a circuit here. A control script is not: the circuit
# states its analyses itself.
BLOCKING = lambda reasons: [r for r in reasons if r not in (".control script", "Verilog-A model")]


def _spice_deck(text: str, gnucap: bool) -> tuple[list, list, dict]:
    """Analyses, outputs and options of a SPICE or gnucap deck, from its dot lines or its
    control script."""
    analysis = _gnucap_analysis if gnucap else spice_analysis
    analyses, outputs, options = [], [], {}
    control = False
    for line in lines(text):
        if line in (".control", ".endc"):
            control = line == ".control"
            continue
        if control:
            head, *args = line.split()
            if head in _SCRIPTED or line.startswith("set appendwrite"):
                raise Unsupported(f"control script: {head}")
            if head in ("op", "tran", "ac", "dc"):
                if (a := spice_analysis(head, args)) not in analyses:
                    analyses.append(a)
            elif head in ("print", "plot", "save", "wrdata", "write"):
                outputs += [s for s in _signals(" ".join(args)) if s not in outputs]
            continue
        if line[0] != "." or len(line) == 1:
            continue
        head, *args = line[1:].split()
        if gnucap and head in _GNUCAP_SCRIPTED:
            raise Unsupported(f"script: .{head}")
        if head in ("op", "tran", "ac", "dc") or (gnucap and head == "tr"):
            if (a := analysis(head, args)) not in analyses:
                analyses.append(a)
        elif head in ("print", "plot", "probe", "save"):
            text = " ".join(args)
            if gnucap:
                text = _MULTI.sub(lambda m: " ".join(f"{m[1]}({n})" for n in m[2].split()), text)
            outputs += [s for s in _signals(text) if s not in outputs]
        elif head == "temp" and args:
            options["temp"] = number(args[0])
        elif head in ("option", "options", "opt", "opts"):
            for a in args:
                key, _, value = a.partition("=")
                if key in OPTIONS and value:
                    options[key] = value if key == "method" else number(value)
    return analyses, outputs, options


def log_sweep(start: float, stop: float, total: int, base: float = 10.0) -> int:
    """Points per decade (base 10) or octave (base 2) of a log sweep stated by its total
    number of points, both ends included. A sweep that does not fall on a whole number
    per decade is not one the other simulators can state."""
    if total < 2 or start <= 0 or stop <= start:
        raise Unsupported(f"log sweep {start} {stop} {total}")
    per = (total - 1) / (math.log(stop / start) / math.log(base))
    if abs(per - round(per)) > 1e-6 * per:
        raise Unsupported(f"log sweep of {total} points: {per:.4g} per "
                          f"{'decade' if base == 10 else 'octave'}")
    return round(per)


# Integration methods by the names the circuit states them in.
_METHODS = {"trap": "trap", "trapezoidal": "trap", "gear": "gear", "gear2": "gear", "bdf": "gear",
            "bdf2": "gear"}


def _keyed(args: list[str], positional: tuple[str, ...]) -> dict[str, str]:
    """``key=value`` arguments, and positional ones by their place, as ahkab and VACASK
    read them; quotes dropped."""
    out, k = {}, 0
    for a in args:
        if "=" in a:
            key, _, value = a.partition("=")
            out[key] = value.strip('"')
        elif k < len(positional):
            out[positional[k]] = a.strip('"')
            k += 1
        else:
            raise Unsupported(f"argument {a!r}")
    return out


def _ahkab_deck(text: str) -> tuple[list, list, dict]:
    """ahkab: ``.op``, ``.dc source= start= stop= step=``, ``.ac [type] nsteps start
    stop`` (``nsteps`` points in all), ``.tran tstep tstop [uic]``, ``.plot``. ``uic=0``
    starts from zero, ``1`` from the operating point, ``2`` from it with the elements'
    initial conditions, which SPICE applies only with ``uic``."""
    analyses, outputs, options = [], [], {}
    for line in lines(text):
        if line[0] != "." or len(line) == 1:
            continue
        head, *args = line[1:].split()
        if head == "op":
            a = {"type": "op"}
        elif head == "dc":
            k = _keyed(args, ("source", "start", "stop", "step"))
            if k.get("type", "lin")[:3] != "lin":
                raise Unsupported(".dc log sweep")
            a = {"type": "dc", "sweep": [{"source": k["source"], "start": number(k["start"]),
                                          "stop": number(k["stop"]), "step": number(k["step"])}]}
        elif head == "ac":
            k = _keyed(args, ("type", "nsteps", "start", "stop"))
            start, stop, n = number(k["start"]), number(k["stop"]), int(number(k["nsteps"]))
            kind = k.get("type", "log")
            if kind == "lin":
                a = {"type": "ac", "sweep": "lin", "points": n, "start": start, "stop": stop}
            elif kind == "log":
                a = {"type": "ac", "sweep": "dec", "points": log_sweep(start, stop, n),
                     "start": start, "stop": stop}
            else:
                raise Unsupported(f".ac type {kind}")
        elif head == "tran":
            k = _keyed(args, ("tstep", "tstop", "uic"))
            uic = int(number(k.get("uic", "0")))
            if uic == 3:
                raise Unsupported(".tran from an .ic label")
            a = {"type": "tran", "step": number(k["tstep"]), "stop": number(k["tstop"])}
            if number(k.get("tstart", "0")):
                a["start"] = number(k["tstart"])
            if uic != 1:
                a["uic"] = True
            method = k.get("method", "")
            if method in _METHODS or method[:4] == "gear":
                options["method"] = _METHODS.get(method, "gear")
        elif head == "plot":
            outputs += [s for s in _signals(" ".join(args[1:])) if s not in outputs]
            continue
        else:
            continue
        if a not in analyses:
            analyses.append(a)
    return analyses, outputs, options


def _josim_deck(text: str) -> tuple[list, list, dict]:
    """JoSIM: ``.tran tstep tstop [pstart [pstep]]`` from zero initial conditions (it has
    no operating point); ``.print``, ``.plot``, ``.save`` of ``nodev a b``, ``devi x``,
    ``devv x`` (the voltage over device x), ``v()``, ``i()``."""
    ls = lines(text)
    nodes: dict[str, tuple[str, str]] = {}
    depth = 0
    for line in ls:
        words = line.split()
        depth += words[0] == ".subckt"
        depth -= words[0] == ".ends"
        if not depth and words[0][0] not in ".#" and len(words) > 2:     # "#": a comment
            nodes[words[0]] = (words[1], words[2])
    analyses, outputs = [], []
    for line in ls:
        head, *args = line.split()
        if head == ".tran":
            nums = [number(a) for a in args if a != "uic"]
            if len(nums) < 2:
                raise Unsupported(".tran without step and stop")
            a = {"type": "tran", "step": nums[0], "stop": nums[1], "uic": True}
            if len(nums) > 2 and nums[2]:
                a["start"] = nums[2]
            if a not in analyses:
                analyses.append(a)
        elif head in (".print", ".plot", ".save") and args:
            kind = args[0]
            if kind == "nodev" and len(args) > 1:
                pair = args[1:3] if len(args) > 2 and args[2] not in ("0", "gnd") else args[1:2]
                found = [f"v({','.join(pair)})"]
            elif kind == "devi" and len(args) > 1 and args[1] in nodes:
                found = [f"i({args[1]})"]
            elif kind == "devv" and len(args) > 1 and args[1] in nodes:
                a, b = nodes[args[1]]
                found = [f"v({a},{b})" if b not in ("0", "gnd") else f"v({a})"]
            else:                                       # v(device): the voltage over it
                found = []
                for s in _signals(" ".join(args)):
                    names = s[2:-1].split(",")
                    if s[0] == "v" and len(names) == 1 and names[0] in nodes:
                        a, b = nodes[names[0]]
                        s = f"v({a},{b})" if b not in ("0", "gnd") else f"v({a})"
                    elif s[0] == "v" and any(n in nodes for n in names):
                        continue
                    found.append(s)
            outputs += [s for s in found if s not in outputs]
    return analyses, outputs, {}


_QUCS_PREFIX = {"E": 18, "P": 15, "T": 12, "G": 9, "M": 6, "k": 3, "m": -3, "u": -6, "n": -9,
                "p": -12, "f": -15}


def qucs_number(text: str) -> float:
    """A qucs value: ``1 pA``, ``10 GHz``, ``4s``, ``1e-16``; ``M`` is mega, ``m`` milli."""
    m = re.fullmatch(r"\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s*([A-Za-z]*)\s*", text)
    if not m:
        raise Unsupported(f"not a number: {text!r}")
    unit = m[2]
    scale = _QUCS_PREFIX.get(unit[:1], 0) if len(unit) > 1 or unit in _QUCS_PREFIX else 0
    if unit in ("F", "m"):                                  # farad; metre is not a prefix
        scale = 0 if unit == "F" else -3
    return float(Decimal(m[1]).scaleb(scale))


def qucs_items(text: str):
    """(type, name, nodes, properties) per component or analysis line of a qucs netlist."""
    for raw in text.splitlines():
        line = raw.strip()
        m = re.match(r"(\.?\w+):(\S+)\s*(.*)", line)
        if not m or line.startswith("#"):
            continue
        rest = m[3]
        props = dict(re.findall(r'(\w+)="([^"]*)"', rest))
        nodes = [t for t in re.sub(r'\w+="[^"]*"', "", rest).split()]
        yield m[1], m[2], nodes, props


def _qucsator_deck(text: str) -> tuple[list, list, dict]:
    """qucsator: ``.DC`` (an operating point), ``.AC`` (log sweeps by their total number
    of points), ``.TR``; a ``.SW`` sweeps a parameter, not a source. Probes are the
    outputs: ``VProbe:p a b`` is v(a,b), ``IProbe:p`` the current i(p)."""
    analyses, outputs, options = [], [], {}
    for kind, name, nodes, props in qucs_items(text):
        if kind == ".SW":
            raise Unsupported("qucsator parameter sweep")
        if kind in (".DC", ".TR"):
            for key, opt in (("Temp", "temp"), ("reltol", "reltol"), ("abstol", "abstol"),
                             ("vntol", "vntol")):
                if key in props:
                    options[opt] = qucs_number(props[key])
        if kind == ".DC":
            a = {"type": "op"}
        elif kind == ".AC":
            start, stop, n = (qucs_number(props[k]) for k in ("Start", "Stop", "Points"))
            if props.get("Type", "lin") == "log":
                a = {"type": "ac", "sweep": "dec", "points": log_sweep(start, stop, int(n)),
                     "start": start, "stop": stop}
            elif props.get("Type", "lin") == "lin":
                a = {"type": "ac", "sweep": "lin", "points": int(n), "start": start, "stop": stop}
            else:
                raise Unsupported(f".AC Type={props.get('Type')}")
        elif kind == ".TR":
            if props.get("Type", "lin") != "lin":
                raise Unsupported(f".TR Type={props.get('Type')}")
            start, stop, n = (qucs_number(props[k]) for k in ("Start", "Stop", "Points"))
            a = {"type": "tran", "step": (stop - start) / (int(n) - 1), "stop": stop}
            if start:
                a["start"] = start
            method = props.get("IntegrationMethod", "").lower()
            if method in _METHODS:
                options["method"] = _METHODS[method]
        else:
            if kind == "VProbe" and len(nodes) >= 2:
                s = f"v({nodes[0]})" if nodes[1] == "gnd" else f"v({nodes[0]},{nodes[1]})"
            elif kind == "IProbe":
                s = f"i({name.lower()})"
            else:
                continue
            if s not in outputs:
                outputs.append(s)
            continue
        if a not in analyses:
            analyses.append(a)
    return analyses, outputs, options


def vacask_split(text: str) -> tuple[list[str], list[str]]:
    """The lines of a VACASK deck outside its control block and inside it, with comments
    and embedded files dropped."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^embed\b.*?^>>>FILE[ \t]*$", "", text, flags=re.S | re.M)
    outside, inside, control = [], [], False
    for raw in text.splitlines():
        line = raw.split("//")[0].rstrip()
        s = line.strip()
        if s in ("control", "endc"):
            control = s == "control"
            continue
        (inside if control else outside).append(line)
    return outside, inside


# VACASK control commands that change the circuit between analyses.
_VACASK_SCRIPTED = {"alter", "var", "reset"}


def _vacask_deck(text: str) -> tuple[list, list, dict]:
    """VACASK: ``analysis name op|tran|ac`` in the control block, a dc sweep as ``sweep
    ... instance="v1" parameter="dc"`` lines before an ``op``; ``options``, ``save``."""
    analyses, outputs, options, sweeps = [], [], {}, []
    for line in vacask_split(text)[1]:
        words = line.split()
        if not words:
            continue
        head, args = words[0], words[1:]
        if head in _VACASK_SCRIPTED:
            raise Unsupported(f"control script: {head}")
        if head == "options":
            for key, value in _keyed(args, ()).items():
                key = {"tran_method": "method"}.get(key, key)
                if key == "method" and value in _METHODS:
                    options["method"] = _METHODS[value]
                elif key in OPTIONS and key != "method":
                    options[key] = number(value)
        elif head == "save":
            outputs += [s for s in _signals(" ".join(args).lower()) if s not in outputs]
        elif head == "sweep":
            k = _keyed(args[1:], ())
            if k.get("parameter", "dc") != "dc" or "instance" not in k or "step" not in k:
                raise Unsupported(f"sweep {' '.join(args)}")
            sweeps.append({"source": k["instance"].lower(), "start": number(k["from"]),
                           "stop": number(k["to"]), "step": number(k["step"])})
        elif head == "analysis" and len(args) >= 2:
            kind, k = args[1], _keyed(args[2:], ())
            if kind == "op" and sweeps:
                a = {"type": "dc", "sweep": sweeps[::-1]}          # the last sweep is inner
            elif sweeps:
                raise Unsupported(f"swept {kind}")
            elif kind == "op":
                a = {"type": "op"}
            elif kind == "tran":
                a = {"type": "tran", "step": number(k["step"]), "stop": number(k["stop"])}
                if number(k.get("start", "0")):
                    a["start"] = number(k["start"])
                if number(k.get("maxstep", "0")):
                    a["max_step"] = number(k["maxstep"])
                if k.get("icmode") == "uic":
                    a["uic"] = True
            elif kind == "ac" and k.get("mode") in ("dec", "oct"):
                a = {"type": "ac", "sweep": k["mode"], "points": int(number(k["points"])),
                     "start": number(k["from"]), "stop": number(k["to"])}
            elif kind == "ac" and k.get("mode") == "lin":
                a = {"type": "ac", "sweep": "lin", "points": int(number(k["points"])) + 1,
                     "start": number(k["from"]), "stop": number(k["to"])}
            else:
                raise Unsupported(f"analysis {kind} {' '.join(args[2:])}")
            sweeps = []
            if a not in analyses:
                analyses.append(a)
    return analyses, outputs, options


_READERS = {"ahkab": _ahkab_deck, "josim": _josim_deck, "qucsator": _qucsator_deck,
            "vacask": _vacask_deck}


def from_deck(case: Case, nl: Netlist) -> dict:
    """A circuit's analyses, outputs and options as the deck states them."""
    text = (case.directory / nl.file).read_text(encoding="latin-1")
    if nl.dialect in _READERS:
        analyses, outputs, options = _READERS[nl.dialect](text)
    elif nl.dialect in SPICE_ORDER + ("gnucap",):
        analyses, outputs, options = _spice_deck(text, nl.dialect == "gnucap")
    else:
        raise Unsupported(f"dialect {nl.dialect}: analysis lines not read yet")
    if not analyses:
        raise Unsupported("no analysis")
    circuit = {"title": case.title, "case": case.id, "source": nl.file}
    if outputs:
        circuit["outputs"] = outputs
    if options:
        circuit["options"] = options
    circuit["analysis"] = analyses
    return circuit


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def proposals() -> tuple[dict[str, dict], list[tuple[str, str]]]:
    """A circuit per core netlist that has none yet; netlists of one case with the same
    file name in different dialects are one circuit with variants."""
    circuits = iter_circuits()
    existing = {c.name for c in circuits}
    taken = {(c.raw["case"], f) for c in circuits
             for f in [c.raw["source"], *c.raw.get("variants", {}).values()]}
    out: dict[str, dict] = {}
    skipped: list[tuple[str, str]] = []
    for case in iter_cases():
        groups: dict[str, list[Netlist]] = {}
        for nl in case.netlists():
            if nl.dialect == "veriloga" or (case.id, nl.file) in taken:
                continue
            if BLOCKING(classify.portability(case.graphs[nl.file])[1]):
                continue
            name = Path(nl.file).name                      # darlington.cir.hspice: .cir
            groups.setdefault(name.removesuffix(f".{nl.dialect}"), []).append(nl)
        for stem, nls in groups.items():
            if len({n.dialect for n in nls}) < len(nls):    # same name, same dialect: separate
                split = {n.file: [n] for n in nls}
            else:
                split = {nls[0].file: nls}
            for file, members in split.items():
                members = sorted(members, key=lambda n: SOURCE_PREFERENCE.index(n.dialect)
                                 if n.dialect in SOURCE_PREFERENCE else len(SOURCE_PREFERENCE))
                src = members[0]
                try:
                    circuit = from_deck(case, src)
                except Unsupported as e:
                    skipped.append((f"{case.id}/{src.file}", str(e)))
                    continue
                if len(members) > 1:
                    circuit["variants"] = {n.dialect: n.file for n in members[1:]}
                single = len(groups) == 1 and len(split) == 1
                name = case.id if single else f"{case.id}-{_slug(Path(file).with_suffix('').as_posix())}"
                if name in out or name in existing:         # d_mos1.lin1.ckt, d_mos1.lin1.spice
                    name = f"{case.id}-{_slug(file)}"
                out[name] = circuit
    return out, skipped


def write(name: str, circuit: dict) -> Path:
    path = CIRCUIT_DIR / f"{name}.toml"
    path.parent.mkdir(exist_ok=True)
    path.write_text(tomli_w.dumps(circuit), encoding="utf-8")
    return path
