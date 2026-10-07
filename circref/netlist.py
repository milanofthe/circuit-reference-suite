"""Just enough netlist reading to check a case: what a file includes or loads, which
analyses it runs, and which instances it places.

Two syntax families. SPICE (ngspice, Xyce, HSPICE, PSpice, gnucap's spice mode, WRspice,
JoSIM): dot cards, ``+`` continuation. Spectre (Spectre, VACASK): keyword statements,
``(node ...)`` lists, ``//`` comments. In both, the first line of a deck is its title.
Qucsator netlists (``Type:Name nodes key="value"``) are read for instances and analyses,
Verilog-A sources only for their modules and ``include`` directives.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

SPICE = ("ngspice", "xyce", "hspice", "pspice", "tspice", "spice3", "gnucap", "wrspice",
         "josim", "ltspice", "ahkab", "spicesharp", "cedarsim")
SPECTRE = ("spectre", "vacask")
QUCS = ("qucsator",)
VERILOGA = ("veriloga",)
DIALECTS = SPICE + SPECTRE + QUCS + VERILOGA
VA_SUFFIXES = (".va", ".vams", ".vh", ".vah", ".include", ".inc_va")

# Supplied by every Verilog-A compiler, never part of a case.
VA_STANDARD = ("disciplines.vams", "constants.vams", "discipline.h", "constants.h",
               "discipline.vams", "constant.vams")

# Model types of ngspice N instances that are built in rather than loaded as OSDI.
NGSPICE_N_BUILTIN = {"nport"}
# Xyce's own Y devices; any other Y<type> is a Verilog-A plugin.
XYCE_Y_BUILTIN = {
    "acc", "adc", "add", "and", "antiwindup", "antiwindupl", "antiwinduplimiter", "awl",
    "battery", "buf", "dac", "delay", "dff", "dltch", "ext", "genext", "ibis", "inv", "jkff",
    "lin", "memristor", "mil", "min", "nand", "neuron", "neuronpop", "nor", "not", "nxor",
    "opamp", "or", "pde", "pgbr", "pgbs", "pggb", "pgtr", "powergrid", "powergridbranch",
    "powergridbusshunt", "powergridgenbus", "powergridtransformer", "rom", "rxn", "synapse",
    "tff", "transline", "xor"}

SPICE_ANALYSES = ("op", "dc", "ac", "tran", "noise", "tf", "pz", "sens", "disto", "four",
                  "pss", "hb", "sp", "step", "mpde", "sampling", "embeddedsampling", "lin")
SPECTRE_ANALYSES = ("op", "dc", "ac", "tran", "noise", "xf", "sp", "stb", "pss", "pac",
                    "pnoise", "pxf", "hb", "hbac", "hbnoise", "sweep", "montecarlo",
                    "dcinc", "dcxf", "acxf", "tf")


@dataclass(frozen=True)
class Ref:
    kind: str           # "include" | "lib" | "osdi" | "va" | "data"
    target: str         # the path exactly as written
    section: str | None
    line: int


@dataclass
class Parsed:
    refs: list[Ref] = field(default_factory=list)
    analyses: list[str] = field(default_factory=list)
    # instance masters per subcircuit; "" is the top level
    instances: dict[str, Counter] = field(default_factory=dict)
    sections: dict[str, list[Ref]] = field(default_factory=dict)
    models: dict[str, str] = field(default_factory=dict)        # .model name -> type
    osdi_devices: set[str] = field(default_factory=set)         # model names of N instances
    va_types: set[str] = field(default_factory=set)             # Xyce Y<type> plugin devices
    modules: set[str] = field(default_factory=set)              # Verilog-A modules defined


def dialect_of(path: Path, inherited: str) -> str:
    return "veriloga" if path.suffix.lower() in VA_SUFFIXES else inherited


def _text(path: Path) -> str:
    return path.read_bytes().decode("latin-1")


def _unquote(s: str) -> str:
    return s.strip().strip("\"'")


_FILE_PARAM = re.compile(r"""\bfile(?:name)?\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\s()]+))""", re.I)


def _data_refs(line: str, n: int) -> list[Ref]:
    """Data files named by a model or instance parameter (nport, filesource, PWL). A bare
    name or an expression is a parameter that holds the file name, not the file."""
    names = (next(g for g in m.groups() if g) for m in _FILE_PARAM.finditer(line))
    return [Ref("data", f, None, n) for f in names if "." in f and "{" not in f]


def _master(tokens: list[str]) -> str | None:
    """The last bare token before the first parameter assignment (``w=1``, ``w = 1``), or
    after the last one: SKY130 writes ``x1 d g s b l={l} w={w} sky130_fd_pr__...``."""
    tokens = re.sub(r"\s*=\s*", "=", " ".join(tokens)).split()
    if len(tokens) > 2 and "=" not in tokens[-1] and any("=" in t for t in tokens[1:-1]):
        return _unquote(tokens[-1]).lower()
    bare = []
    for t in tokens:
        if "=" in t or t.lower() in ("params:", "parameters:"):
            break
        bare.append(t)
    return _unquote(bare[-1]).lower() if len(bare) >= 2 else None


# ---------------------------------------------------------------- SPICE family

def _spice_lines(text: str, deck: bool) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    for n, raw in enumerate(text.splitlines(), 1):
        if deck and n == 1:
            continue                                    # title
        line = raw.strip()
        if not line or line[0] == "*":
            continue
        line = re.split(r"\s;|^;|\s\$\s|\s\$$|\s//", line, maxsplit=1)[0].rstrip()
        if not line:
            continue
        if line[0] == "+" and out:
            out[-1] = (out[-1][0], out[-1][1] + " " + line[1:].strip())
        else:
            out.append((n, line))
    return out


def _spice(text: str, deck: bool, dialect: str) -> Parsed:
    bare_commands = dialect == "gnucap"
    p = Parsed(instances={"": Counter()})
    stack = [""]
    section = None
    control = False
    for n, line in _spice_lines(text, deck):
        tokens = line.split()
        head = tokens[0].lower()
        refs = p.sections.setdefault(section, []) if section else p.refs
        if control:
            if head == ".endc":
                control = False
            elif head in ("pre_osdi", "osdi") and len(tokens) > 1:
                refs.append(Ref("osdi", _unquote(tokens[1]), None, n))
            elif head in SPICE_ANALYSES:
                p.analyses.append(head)
            continue
        if head == ".control":
            control = True
        elif head in (".include", ".inc", ".incl"):
            refs.append(Ref("include", _unquote(line.split(None, 1)[1]), None, n))
        elif head == ".lib":
            if len(tokens) == 2:
                section = tokens[1].lower()
            elif len(tokens) >= 3:
                refs.append(Ref("lib", _unquote(tokens[1]), tokens[2].lower(), n))
        elif head == ".endl":
            section = None
        elif head == ".model" and len(tokens) > 2:
            p.models[tokens[1].lower()] = tokens[2].split("(")[0].lower()
            refs += _data_refs(line, n)
        elif head == ".hdl" and len(tokens) > 1:
            refs.append(Ref("va", _unquote(tokens[1]), None, n))
        elif head in (".subckt", ".macro") and len(tokens) > 1:
            stack.append(tokens[1].lower())
            p.instances.setdefault(stack[-1], Counter())
        elif head in (".ends", ".eom"):
            if len(stack) > 1:
                stack.pop()
        elif head[0] == "." and head[1:] in SPICE_ANALYSES:
            p.analyses.append(head[1:])
        elif bare_commands and head in SPICE_ANALYSES:
            p.analyses.append(head)
        elif head[0].isalpha():
            if head[0] == "n" and dialect == "ngspice" and (model := _master(tokens)):
                p.osdi_devices.add(model)
            if head[0] == "y" and dialect == "xyce" and head[1:] not in XYCE_Y_BUILTIN:
                p.va_types.add(head[1:])
            master = _master(tokens) if head[0] == "x" else None
            p.instances[stack[-1]][f"x:{master}" if master else head[0]] += 1
            refs += _data_refs(line, n)
    return p


# ------------------------------------------------------------- Spectre family

_SPECTRE_SKIP = ("model", "parameters", "options", "global", "ground", "save", "simulator",
                 "library", "endlibrary", "endsection", "statistics", "real", "print",
                 "postprocess", "var", "sweep", "alter", "altergroup", "ic", "nodeset",
                 "set", "info", "inline")


def _spectre_lines(text: str, deck: bool) -> list[tuple[int, str]]:
    out: list[tuple[int, str]] = []
    pending, depth, start = "", 0, 0
    heredoc = None
    for n, raw in enumerate(text.splitlines(), 1):
        if deck and n == 1:
            continue                                    # title
        if heredoc:
            if raw.strip() == heredoc:
                heredoc = None
            continue
        line = raw.split("//", 1)[0].rstrip()
        if not pending and line.lstrip().startswith("*"):
            continue
        m = re.search(r"<<<(\w+)\s*$", line)
        if m:
            heredoc, line = m.group(1), line[:m.start()]
        cont = line.endswith("\\")
        line = line.rstrip("\\")
        if not pending:
            start = n
        pending = f"{pending} {line}".strip()
        depth += line.count("(") - line.count(")")
        if pending and not cont and depth <= 0:
            out.append((start, pending))
            pending, depth = "", 0
    if pending:
        out.append((start, pending))
    return out


def _spectre(text: str, deck: bool) -> Parsed:
    p = Parsed(instances={"": Counter()})
    stack = [""]
    section = None
    for n, line in _spectre_lines(text, deck):
        tokens = line.replace("(", " ( ").replace(")", " ) ").split()
        head = tokens[0].lower()
        refs = p.sections.setdefault(section, []) if section else p.refs
        if head in ("include", "ahdl_include", "load") and len(tokens) > 1:
            kind = {"include": "include", "ahdl_include": "va", "load": "osdi"}[head]
            sect = re.search(r"section\s*=\s*(\w+)", line)
            refs.append(Ref("lib" if sect else kind, _unquote(tokens[1]),
                            sect.group(1).lower() if sect else None, n))
        elif head == "section" and len(tokens) > 1:
            section = tokens[1].lower()
        elif head == "endsection":
            section = None
        elif head in ("subckt", "inline") and len(tokens) > 1:
            name = tokens[2] if head == "inline" else tokens[1]
            stack.append(name.lower())
            p.instances.setdefault(stack[-1], Counter())
        elif head == "ends":
            if len(stack) > 1:
                stack.pop()
        elif head == "analysis" and len(tokens) > 2:
            p.analyses.append(tokens[2].lower())
        elif head == "model":
            refs += _data_refs(line, n)
        elif head in ("control", "endc", "embed") or head in _SPECTRE_SKIP:
            continue
        else:
            bare = [t for t in tokens if t not in ("(", ")")]
            master = _master(bare)
            if master in SPECTRE_ANALYSES:
                p.analyses.append(master)
            elif master:
                p.instances[stack[-1]][f"x:{master}"] += 1
                refs += _data_refs(line, n)
    return p


# ------------------------------------------------------------------- Qucsator

_QUCS_ANALYSES = {"dc": "dc", "ac": "ac", "tr": "tran", "sp": "sp", "sw": "sweep", "hb": "hb",
                  "noise": "noise"}


def _qucs(text: str) -> Parsed:
    p = Parsed(instances={"": Counter()})
    stack = [""]
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line or line[0] == "#":
            continue
        kind, _, name = line.split()[0].partition(":")
        kind = kind.lower()
        if kind == ".def":
            if name.lower() == "end":
                if len(stack) > 1:
                    stack.pop()
            else:
                stack.append(name.lower())
                p.instances.setdefault(stack[-1], Counter())
        elif kind[0] == ".":
            p.analyses.append(_QUCS_ANALYSES.get(kind[1:], kind[1:]))
        elif kind == "sub" and (m := re.search(r'\bType="([^"]+)"', line)):
            p.instances[stack[-1]][f"x:{m.group(1).lower()}"] += 1
        elif kind != "eqn":
            p.instances[stack[-1]][kind] += 1
        p.refs += _data_refs(line, n)
    return p


# ------------------------------------------------------------------ Verilog-A

def _veriloga(text: str) -> Parsed:
    p = Parsed(instances={"": Counter()})
    for n, line in enumerate(text.splitlines(), 1):
        if m := re.match(r"\s*module\s+(\w+)", line):
            p.modules.add(m.group(1).lower())
        m = re.match(r'\s*`include\s+"([^"]+)"', line)
        if m and Path(m.group(1)).name not in VA_STANDARD:
            p.refs.append(Ref("va", m.group(1), None, n))
    return p


@lru_cache(maxsize=None)
def parse(path: Path, dialect: str, deck: bool = False) -> Parsed:
    """Parsed once per run; callers must not modify the result."""
    text = _text(path)
    if dialect in SPICE:
        return _spice(text, deck, dialect)
    if dialect in SPECTRE:
        return _spectre(text, deck)
    if dialect in QUCS:
        return _qucs(text)
    return _veriloga(text)


def flat_count(subckts: dict[str, Counter]) -> int:
    """Instances once every subcircuit defined in ``subckts`` is expanded. A master
    defined elsewhere (a PDK device, a compiled model) counts as one device."""
    memo: dict[str, int] = {}

    def count(name: str, seen: tuple[str, ...]) -> int:
        if name in memo:
            return memo[name]
        total = 0
        for key, k in subckts[name].items():
            master = key[2:] if key.startswith("x:") else None
            if master in subckts and master not in seen:
                total += k * count(master, seen + (master,))
            else:
                total += k
        memo[name] = total
        return total

    return count("", ("",))
