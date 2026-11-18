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


def from_deck(case: Case, nl: Netlist) -> dict:
    """A circuit's analyses, outputs and options as the deck states them, in its dot lines
    or in its control script."""
    if nl.dialect not in SPICE_ORDER + ("gnucap",):
        raise Unsupported(f"dialect {nl.dialect}: analysis lines not read yet")
    gnucap = nl.dialect == "gnucap"
    analysis = _gnucap_analysis if gnucap else spice_analysis
    analyses, outputs, options = [], [], {}
    control = False
    for line in lines((case.directory / nl.file).read_text(encoding="latin-1")):
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
    taken = {(c.raw["case"], f) for c in iter_circuits()
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
                out[name] = circuit
    return out, skipped


def write(name: str, circuit: dict) -> Path:
    path = CIRCUIT_DIR / f"{name}.toml"
    path.parent.mkdir(exist_ok=True)
    path.write_text(tomli_w.dumps(circuit), encoding="utf-8")
    return path
