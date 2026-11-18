"""A circuit body from one SPICE dialect into another.

A staged body (the top-level deck and the files it includes) is rewritten in place. Each
file is read into statements: continuation lines joined, comments kept, every token with
the text in front of it, so that a statement no rule touches is written back byte for
byte. The rules of the dialect pair are applied statement by statement; what the target
has no equivalent for raises Untranslatable, naming the construct.

Where a difference is a mapping it is data below: model levels and versions per device,
model types, expression functions, source forms, comment marks, ground names. Every entry
is taken from the simulators' documentation and source: Xyce Reference Guide 7.9 and Xyce
7.10 (``registerDevice``, ``ExpressionLexer.l``, ``ExpressionParser.yxx``,
``N_DEV_SourceData.C``), ngspice manual and ngspice 47 (``inpdomod.c``, ``inpptree.c``,
``ptfuncs.c``, ``numparam/xpressn.c``, ``inpcom.c``).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

from .adapters import NOT_BODY
from .circuit import Unsupported, number
from .entry import Case, Netlist
from .netlist import VA_SUFFIXES
from .stage import staged


class Untranslatable(Exception):
    """A construct of the source dialect without an equivalent in the target dialect."""


# Dialects read with the rules of another: SPICE3 decks are ngspice decks.
FAMILY = {"ngspice": "ngspice", "spice3": "ngspice", "xyce": "xyce"}

# Inline comment marks. ngspice: ``;`` anywhere, ``$`` after a blank or comma, ``//``
# (inp_stripcomments_line); Xyce: ``;`` only (SpiceSeparatedFieldTool).
COMMENT = {"ngspice": (";", "$", "//"), "xyce": (";",)}

# Node names that are ground besides 0. ngspice: ``gnd`` (inp_fix_gnd_name). Xyce: GND,
# GND! and GROUND, but only under ``.preprocess replaceground true``.
GROUND = {"ngspice": ("gnd",), "xyce": ("gnd", "gnd!", "ground")}

# Model types with a device family and level; the rest map by name or not at all.
FAMILY_OF_TYPE = {"nmos": "mos", "pmos": "mos", "npn": "bjt", "pnp": "bjt", "d": "diode",
                  "njf": "jfet", "pjf": "jfet", "nmf": "mesfet", "pmf": "mesfet",
                  "r": "r", "res": "r"}

# The model a (family, level) selects. Levels absent here have no counterpart in the
# other dialect. Xyce: Reference Guide table 2-36 and registerDevice; ngspice: inpdomod.c.
LEVELS = {
    "xyce": {
        ("mos", 1): "mos1", ("mos", 2): "mos2", ("mos", 3): "mos3", ("mos", 6): "mos6",
        ("mos", 9): "bsim3", ("mos", 49): "bsim3", ("mos", 14): "bsim4", ("mos", 54): "bsim4",
        ("mos", 10): "BSIMSOI 3.2", ("mos", 57): "BSIMSOI 3.2", ("mos", 18): "Xyce VDMOS",
        ("mos", 70): "BSIMSOI 4.6.1", ("mos", 70450): "BSIMSOI 4.5.0",
        ("mos", 70470): "BSIMSOI 4.7.0", ("mos", 77): "BSIM6",
        ("mos", 102): "PSP 102", ("mos", 103): "PSP 103", ("mos", 1031): "PSP 103 thermal",
        ("mos", 107): "BSIM-CMG 107", ("mos", 108): "BSIM-CMG 108", ("mos", 110): "BSIM-CMG 110",
        ("mos", 111): "BSIM-CMG 111", ("mos", 260): "EKV 2.6", ("mos", 301): "EKV 3",
        ("mos", 2000): "MVS ETSOI", ("mos", 2001): "MVS HEMT", ("mos", 2002): "MVSG",
        ("mos", 10240): "L-UTSOI",
        ("bjt", 1): "gummel-poon", ("bjt", 11): "VBIC 1.3", ("bjt", 12): "VBIC 1.3 4T",
        ("bjt", 23): "FBH HBT", ("bjt", 230): "HICUM L0", ("bjt", 234): "HICUM L2 2.34",
        ("bjt", 504): "Mextram 504", ("bjt", 505): "Mextram 504 thermal",
        ("diode", 1): "diode", ("diode", 2): "PSpice diode", ("diode", 200): "JUNCAP200",
        ("diode", 2002): "diode_cmc",
        ("jfet", 1): "jfet", ("jfet", 2): "Shockley JFET",
        # Xyce's MESFET has exactly the parameter set of SPICE3's Statz model.
        ("mesfet", 1): "statz",
        ("r", 1): "resistor", ("r", 2): "thermal resistor",
    },
    "ngspice": {
        ("mos", 1): "mos1", ("mos", 2): "mos2", ("mos", 3): "mos3", ("mos", 4): "BSIM1",
        ("mos", 5): "BSIM2", ("mos", 6): "mos6", ("mos", 7): "MOS7", ("mos", 8): "bsim3",
        ("mos", 49): "bsim3", ("mos", 9): "MOS9", ("mos", 14): "bsim4", ("mos", 54): "bsim4",
        ("mos", 15): "BSIM5", ("mos", 10): "BSIMSOI 4.4", ("mos", 58): "BSIMSOI 4.4",
        ("mos", 55): "BSIM3SOI-FD 2.1", ("mos", 56): "BSIM3SOI-DD 2.1",
        ("mos", 57): "BSIM3SOI-PD 2.2", ("mos", 60): "SOI3", ("mos", 68): "HiSIM2",
        ("mos", 73): "HiSIM_HV",
        ("bjt", 0): "gummel-poon", ("bjt", 1): "gummel-poon", ("bjt", 4): "VBIC 1.2",
        ("bjt", 9): "VBIC 1.2", ("bjt", 8): "HICUM L2 2.40",
        ("diode", 1): "diode", ("diode", 3): "geometric diode",
        ("jfet", 1): "jfet", ("jfet", 2): "Parker-Skellern JFET",
        ("mesfet", 1): "statz", ("mesfet", 2): "MESA", ("mesfet", 3): "MESA",
        ("mesfet", 4): "MESA", ("mesfet", 5): "HFET1", ("mesfet", 6): "HFET2",
        ("r", 1): "resistor",
    },
}

# Model types each dialect knows, besides FAMILY_OF_TYPE, and the ones that are spelled
# differently. ngspice: inpdomod.c; Xyce: registerModelType.
TYPES = {
    "xyce": {"c", "cap", "l", "ind", "ltra", "vswitch", "iswitch", "switch", "core", "zod",
             "dig", "transline", "memristor", "pde", "rom", "lin", "opamp", "adc", "dac",
             "neuron", "neuronpop", "synapse", "rxn", "min", "mil", "delay", "genext", "ext",
             "battery"},
    "ngspice": {"c", "l", "ltra", "sw", "csw", "urc", "txl", "cpl", "vdmos", "vdmosn", "vdmosp",
                "nsoi", "psoi", "numd", "nbjt", "numos", "nhfet", "phfet"},
}
TYPE_NAMES = {("xyce", "ngspice"): {"cap": "c", "ind": "l"}}

# Model parameters of R, C and L that differ in meaning: in Xyce R, C and L multiply the
# instance value (Reference Guide tables 2-38, 2-40, 2-43); in ngspice r and res are the
# value of an instance that states none, cap and ind the model's value (res.c, cap.c,
# ind.c), and c of a capacitor model is not a parameter.
PASSIVE_VALUE = {"r": ("r", "res"), "res": ("r", "res"), "c": ("c", "cap"),
                 "cap": ("c", "cap"), "l": ("l", "ind"), "ind": ("l", "ind")}

# What a version parameter selects, per model and dialect: the version computed for a
# card that states ``version`` (normalized to "a.b.c"), or for one that does not (None).
# Xyce BSIM3 computes 3.2.2 whatever the card says (N_DEV_MOSFET_B3.C); Xyce BSIM4
# 4.6.1, 4.7.0 or 4.8.2 (checkAndFixVersion_); ngspice BSIM3 3.0, 3.1, 3.2.2-3.2.4 or 3.3.0
# (inpdomod.c, b3v32set.c), BSIM4 4.5, 4.6, 4.7 or 4.8.0-4.8.3 (b4set.c).
def _xyce_bsim4(v):
    if v is None or v >= (4, 8):
        return (4, 8, 2)
    return (4, 7, 0) if v >= (4, 7) else (4, 6, 1)


def _ngspice_bsim3(v):
    if v is None or v[:2] == (3, 3):
        return (3, 3, 0)
    if v[:2] == (3, 2):
        return v if v[2] in (2, 3, 4) else (3, 2, 4)
    return v[:2] + (0,)


def _ngspice_bsim4(v):
    if v is None:
        return (4, 8, 3)
    if v[:2] == (4, 8):
        return v if v[2] <= 3 else (4, 8, 3)
    return v[:2] + (0,) if v[:2] >= (4, 6) else (4, 5, 0)


VERSIONS = {
    ("xyce", "bsim3"): lambda v: (3, 2, 2),
    ("xyce", "bsim4"): _xyce_bsim4,
    ("ngspice", "bsim3"): _ngspice_bsim3,
    ("ngspice", "bsim4"): _ngspice_bsim4,
}

# Expression functions with another name or form in the target. A string is the target
# name, a callable builds the target text from the translated arguments, None has no
# equivalent. Forms are chosen so that they hold in both of ngspice's expression parsers
# (numparam for parameters, inpptree for behavioral sources), which disagree on pwr.
#   Xyce: log is log10, pwr and pow are pow, pwrs is the signed power, stp(x) is x > 0,
#   if(c, a, b), limit(x, lo, hi), sign(x, y) is |x| with the sign of y, int truncates.
#   ngspice: log and ln are ln, pwr is the signed power in inpptree and |x|^y in numparam,
#   u(x) is x > 0, ternary_fcn(c, a, b), limit(nom, var) is random, int truncates.
def _ternary(c, a, b):
    return f"(({c}) ? ({a}) : ({b}))"


def _table(x, *pairs):
    """Xyce TABLE holds its end values outside the table; ngspice's pwl extrapolates the
    end segments, and exists in behavioral expressions only."""
    if len(pairs) < 4 or len(pairs) % 2:
        raise Untranslatable("table() with fewer than two points")
    points = list(zip(pairs[::2], pairs[1::2]))
    try:
        points.sort(key=lambda p: number(p[0]))
    except Unsupported:
        pass                                    # parameters: written in order
    (x0, y0), (xn, yn) = points[0], points[-1]
    inner = f"pwl({x}, {', '.join(f'{a}, {b}' for a, b in points)})"
    return _ternary(f"{x}) < ({x0}", y0, _ternary(f"{x}) > ({xn}", yn, inner))


FUNCTIONS = {
    ("xyce", "ngspice"): {
        "log": "log10",
        "pwr": "pow",
        "pwrs": lambda x, y: _ternary(f"{x}) >= (0", f"pow({x}, {y})", f"-pow(-({x}), {y})"),
        "if": _ternary,
        "stp": lambda x: _ternary(f"{x}) > (0", "1", "0"),
        "uramp": lambda x: _ternary(f"{x}) > (0", x, "0"),
        "limit": lambda x, lo, hi=None: x if hi is None else f"min(max({x}, {lo}), {hi})",
        "table": _table,
        "sign": lambda x, y: _ternary(f"{y}) >= (0", f"abs({x})", f"-abs({x})"),
        "int": lambda x: _ternary(f"{x}) >= (0", f"floor({x})", f"ceil({x})"),
        "arctan": "atan",
        # Without a UQ analysis Xyce's random functions return their mean (Reference
        # Guide, table 2-33 note 1); ngspice draws a random number.
        "agauss": lambda mu, *_: mu, "gauss": lambda mu, *_: mu, "aunif": lambda mu, *_: mu,
        "unif": lambda mu, *_: mu, "rand": lambda: "0.5",
        "atan2": None, "fmod": None, "sdt": None, "ddx": None, "fasttable": None,
        "spline": None, "akima": None, "cubic": None, "wodicka": None, "bli": None,
        "tablefile": None, "schedule": None,
    },
    ("ngspice", "xyce"): {
        "log": "ln",
        "ternary_fcn": _ternary,
        "u": "stp",
        "sqr": lambda x: f"(({x})*({x}))",
        "u2": lambda x: _ternary(f"{x}) > (1", "1", _ternary(f"{x}) > (0", x, "0")),
        "eq0": lambda x: _ternary(f"{x}) == (0", "1", "0"),
        "ne0": lambda x: _ternary(f"{x}) != (0", "1", "0"),
        "gt0": lambda x: _ternary(f"{x}) > (0", "1", "0"),
        "lt0": lambda x: _ternary(f"{x}) < (0", "1", "0"),
        "ge0": lambda x: _ternary(f"{x}) >= (0", "1", "0"),
        "le0": lambda x: _ternary(f"{x}) <= (0", "1", "0"),
        "pwl": None, "pwl_derivative": None, "limit": None, "vec": None, "var": None,
    },
}
# Signal accessors in expressions; the devices whose current ngspice's expressions read.
PROBES = {"v", "i", "vr", "vi", "vm", "vp", "vdb", "ir", "ii", "im", "ip", "idb"}
BRANCH_NGSPICE = ("v", "e", "h", "l")
# pwr in ngspice: signed power in behavioral expressions, |x|^y in parameters.
PWR_NGSPICE = {True: "pwrs", False: lambda x, y: f"pow(abs({x}), {y})"}

# Transient source functions. Xyce: getSourceFunctionID; ngspice: vsrc.c, isrc.c.
SOURCE_FUNCTIONS = {
    "xyce": {"pulse", "sin", "exp", "sffm", "pwl", "pat"},
    "ngspice": {"pulse", "sin", "sine", "exp", "sffm", "pwl", "am", "trnoise", "trrandom"},
}
SOURCE_NAMES = {("ngspice", "xyce"): {"sine": "sin"}}

# Dot commands of the body with another name in the target, and the ones it has no
# equivalent for. NOT_BODY lines (analyses, outputs) are dropped, as in a deck.
DOTS = {
    ("xyce", "ngspice"): {".global_param": ".param", ".dcvolt": ".ic", ".incl": ".include"},
    ("ngspice", "xyce"): {".incl": ".include"},
}
# Bookkeeping of the source dialect that is not part of the circuit: dropped with its block.
DROP = {
    "xyce": {".data": ".enddata", ".fft": None, ".pce": None, ".result": None,
             ".objective": None, ".rol": None, ".mor": None, ".embeddedsampling": None,
             ".probe/csd": None},
    "ngspice": {".control": ".endc", ".csparam": None, ".width": None},
}
# Options that change what the circuit is, as the target states them; None: the target
# has no equivalent. Every other option sets up the solver or the output and is dropped,
# and the circuit's own (circuit.OPTIONS) the adapter states. Xyce groups its options
# (.options parser scale=1u); ngspice does not (.options scale=1u).
#   Xyce Reference Guide 2.1.25: parser SCALE, MODEL_BINNING (default true; ngspice always
#   bins). ngspice manual 11.1: scale, defad/defas/defl/defw (MOS defaults), rshunt,
#   cshunt, rseries (elements added to every node or inductor).
OPTION_MAP = {
    ("xyce", "ngspice"): {"scale": "scale", "model_binning=false": None},
    ("ngspice", "xyce"): {"scale": "parser scale", "defad": None, "defas": None, "defl": None,
                          "defw": None, "rshunt": None, "cshunt": None, "rseries": None},
}
OPTION_LINES = (".options", ".option", ".opt", ".opts")

NO_DOT = {
    "ngspice": {".if": "conditional netlist (.if)", ".elseif": "conditional netlist (.if)",
                ".else": "conditional netlist (.if)", ".endif": "conditional netlist (.if)"},
    "xyce": {},
}

# Elements of the source dialect the target has no equivalent for, by first letter.
NO_ELEMENT = {
    ("xyce", "ngspice"): {"y": "Xyce Y device", "u": "Xyce digital device",
                          "n": "Xyce N device", "p": "Xyce port device",
                          "s": "voltage switch (Xyce switches transition smoothly, ngspice's do not)",
                          "w": "current switch (Xyce switches transition smoothly, ngspice's do not)"},
    ("ngspice", "xyce"): {"a": "XSPICE code model", "n": "OSDI device", "p": "coupled lines (P)",
                          "y": "lossy line (Y)", "u": "RC line (U)",
                          "s": "voltage switch (Xyce switches transition smoothly, ngspice's do not)",
                          "w": "current switch (Xyce switches transition smoothly, ngspice's do not)"},
}

# Terminals of an element before its value or model; X and K are positional to the end.
NODES = {"r": 2, "c": 2, "l": 2, "v": 2, "i": 2, "b": 2, "e": 4, "g": 4, "f": 2, "h": 2,
         "d": 2, "j": 3, "z": 3, "q": 3, "m": 4, "t": 4, "o": 4}

# ------------------------------------------------------------------------- statements

@dataclass
class Token:
    ws: str         # what precedes the token: blanks, continuation marks, comments
    text: str


@dataclass
class Statement:
    raw: str                                    # as written, continuation lines included
    tokens: list[Token] = field(default_factory=list)
    tail: str = ""                              # after the last token, newline included
    edited: bool = False
    title: bool = False

    @property
    def head(self) -> str:
        return self.tokens[0].text.lower() if self.tokens else ""

    def words(self) -> list[str]:
        return [t.text.lower() for t in self.tokens]

    def render(self, marks: tuple[str, ...]) -> str:
        if self.title:
            return self.raw
        if not self.tokens:
            return _comment_lines(self.raw, marks)
        parts = [(_comments(t.ws, marks), t.text) for t in self.tokens]
        tail = _comments(self.tail, marks)
        if not self.edited and tail == self.tail and all(w == t.ws for (w, _), t in
                                                          zip(parts, self.tokens)):
            return self.raw
        return "".join(w + x for w, x in parts) + tail

    def set(self, i: int, text: str) -> None:
        self.tokens[i].text = text
        self.edited = True


def _comment_at(s: str, i: int, marks: tuple[str, ...]) -> bool:
    if ";" in marks and s[i] == ";":
        return True
    if "$" in marks and s[i] == "$" and (i == 0 or s[i - 1] in " \t,"):
        return True
    return "//" in marks and s.startswith("//", i)


def _comments(ws: str, marks: tuple[str, ...]) -> str:
    """The comments in the text between two tokens written with the target's marks: an
    inline comment with its first mark, a comment line with ``*``."""
    if all(m in marks for m in ALL_MARKS):
        return ws
    lines = ws.split("\n")
    for k, line in enumerate(lines):
        s = line.lstrip(" \t")
        if k and s[:1] == "*":
            continue
        if k and s[:1] not in ("", "+"):                # a comment line between continuations
            lines[k] = line[:len(line) - len(s)] + "*" + s
            continue
        m = re.search(r"\$|//", line)
        if m and ";" not in line[:m.start()]:
            lines[k] = line[:m.start()] + marks[0] + line[m.end():]
    return "\n".join(lines)


def _comment_lines(text: str, marks: tuple[str, ...]) -> str:
    """Comment and blank lines with the target's marks: ``*`` for a whole line."""
    if all(m in marks for m in ALL_MARKS):
        return text
    out = []
    for line in text.splitlines(keepends=True):
        s = line.lstrip(" \t")
        if s[:1] not in ("", "*", "\n", "\r"):
            line = line[:len(line) - len(s)] + "*" + s
        out.append(line)
    return "".join(out)


ALL_MARKS = {m for marks in COMMENT.values() for m in marks}


def _close(s: str, i: int) -> int:
    """The index after the brace that closes the one at ``i``."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return j + 1
    return len(s)


_BREAK = set(" \t\r\n(){},='\"")


def tokenize(raw: str, marks: tuple[str, ...]) -> tuple[list[Token], str]:
    toks: list[Token] = []
    i, n, ws = 0, len(raw), 0
    line_start = True
    while i < n:
        c = raw[i]
        if c == "\n":
            i += 1
            line_start = True
            continue
        if line_start:
            line_start = False
            j = i
            while j < n and raw[j] in " \t\r":
                j += 1
            if toks and j < n and raw[j] == "+":
                i = j + 1
                continue
            if toks and j < n and (raw[j] == "*" or _comment_at(raw, j, marks)):
                k = raw.find("\n", j)
                i = n if k < 0 else k
                continue
            i = j
            continue
        if c in " \t\r":
            i += 1
            continue
        if _comment_at(raw, i, marks):
            k = raw.find("\n", i)
            i = n if k < 0 else k
            continue
        start = i
        if c == "{":
            i = _close(raw, i)
        elif c in "'\"":
            k = raw.find(c, i + 1)
            i = n if k < 0 else k + 1
        elif c in "()=,}":
            i += 1
        else:
            while i < n and raw[i] not in _BREAK and not _comment_at(raw, i, marks):
                i += 1
        toks.append(Token(raw[ws:start], raw[start:i]))
        ws = i
    return toks, raw[ws:]


def parse(text: str, dialect: str, deck: bool) -> list[Statement]:
    """Statements of a file; comment and blank lines are statements without tokens. The
    first line of a deck is its title."""
    marks = COMMENT[FAMILY[dialect]]
    lines = text.splitlines(keepends=True)
    out: list[Statement] = []
    if deck and lines:
        out.append(Statement(lines.pop(0), title=True))
    current: Statement | None = None
    pending = ""
    for line in lines:
        s = line.lstrip()
        if s.startswith("+") and current is not None:
            current.raw += pending + line
            pending = ""
        elif not s.strip() or s[0] == "*" or _comment_at(s, 0, marks):
            pending += line
        else:
            if current is not None:
                out.append(current)
            if pending:
                out.append(Statement(pending))
                pending = ""
            current = Statement(line)
    if current is not None:
        out.append(current)
    if pending:
        out.append(Statement(pending))
    for st in out[1 if deck else 0:]:
        if st.raw.lstrip() and st.raw.lstrip()[0] != "*" and not _comment_at(st.raw.lstrip(), 0, marks):
            st.tokens, st.tail = tokenize(st.raw, marks)
    return out


# ------------------------------------------------------------------------ expressions

_IDENT = re.compile(r"[A-Za-z_][\w.!]*")
_NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:e[-+]?\d+)?[a-z]*$", re.I)


def is_number(token: str) -> bool:
    return bool(_NUMBER.match(token))


def _split_args(s: str) -> list[str]:
    args, depth, start = [], 0, 0
    for i, c in enumerate(s):
        if c in "({":
            depth += 1
        elif c in ")}":
            depth -= 1
        elif c == "," and depth == 0:
            args.append(s[start:i])
            start = i
            start += 1
    args.append(s[start:])
    return [a.strip() for a in args]


@dataclass
class Context:
    """What the files of a body define, read before any is translated."""
    params: set[str] = field(default_factory=set)
    globals: set[str] = field(default_factory=set)                  # .param at the top level
    models: dict[str, tuple[str, str | None]] = field(default_factory=dict)   # name -> type, level
    declared: dict[str, set[str]] = field(default_factory=dict)     # subckt -> its parameters
    inner: dict[str, set[str]] = field(default_factory=dict)        # subckt -> .param inside
    passed: dict[str, set[str]] = field(default_factory=dict)       # subckt -> X line parameters
    multiplier: dict[str, str | None] = field(default_factory=dict)  # Xyce R/C/L model -> R/C/L
    replace_ground: bool = False                # Xyce .preprocess replaceground true
    hspice_math: bool = False                   # Xyce .options parser hspice_ext with math


class Translator:
    def __init__(self, source: str, target: str):
        if source not in FAMILY or target not in FAMILY:
            raise Untranslatable(f"no translation from {source} to {target}")
        self.src, self.tgt = FAMILY[source], FAMILY[target]
        self.pair = (self.src, self.tgt)
        self.ctx = Context()
        self.file = Path()                      # the file being translated

    # ----------------------------------------------------------------- context

    def read_context(self, statements: list[Statement]) -> None:
        sub = None
        for st in statements:
            w = st.words()
            if not w:
                continue
            assigned = {w[i - 1] for i in range(2, len(w)) if w[i] == "="}
            if w[0] in (".param", ".global_param"):
                self.ctx.params |= assigned
                if sub is None or w[0] == ".global_param":
                    self.ctx.globals |= assigned
                else:
                    self.ctx.inner.setdefault(sub, set()).update(assigned)
            elif w[0] in (".subckt", ".macro") and len(w) > 1:
                sub = w[1]
                self.ctx.params |= assigned
                self.ctx.declared[sub] = assigned
            elif w[0] in (".ends", ".eom"):
                sub = None
            elif w[0][0] == "x":
                name, _ = _subckt_of(w)
                self.ctx.passed.setdefault(name, set()).update(assigned - {"m"})
            elif w[0] == ".model" and len(w) > 2:
                level = next((w[i + 2] for i in range(3, len(w) - 2)
                              if w[i] == "level" and w[i + 1] == "="), None)
                if self.src == "xyce" and w[2] in PASSIVE_VALUE:
                    self.ctx.multiplier[w[1]] = next(
                        (st.tokens[i + 2].text for i in range(3, len(w) - 2)
                         if w[i] == PASSIVE_VALUE[w[2]][0] and w[i + 1] == "="), None)
                self.ctx.models[w[1].split(".")[0] if "." in w[1] and w[1].split(".")[-1].isdigit()
                                else w[1]] = (w[2], level)
            elif w[0] == ".preprocess" and w[1:3] == ["replaceground", "true"]:
                self.ctx.replace_ground = True
            elif w[0] in (".options", ".option") and "parser" in w and "hspice_ext" in w:
                k = w.index("hspice_ext")
                if k + 2 < len(w) and w[k + 1] == "=" and ("math" in w[k + 2] or "all" in w[k + 2]):
                    self.ctx.hspice_math = True

    def model(self, name: str) -> bool:
        n = name.lower()
        return n in self.ctx.models or n.split(".")[0] in self.ctx.models

    # ------------------------------------------------------------- expressions

    def expr(self, text: str, behavioral: bool) -> str:
        """An expression with the target's functions and operators."""
        table = FUNCTIONS[self.pair]
        out, i, n = [], 0, len(text)
        while i < n:
            c = text[i]
            if c == "^" and self.src == "xyce" and not self.ctx.hspice_math:
                raise Untranslatable("^ is XOR in a Xyce expression")
            if c == "^" and self.tgt == "xyce":
                out.append("**")
                i += 1
                continue
            m = _IDENT.match(text, i) if (c.isalpha() or c == "_") and \
                (i == 0 or not (text[i - 1].isalnum() or text[i - 1] in "_.")) else None
            if not m:
                out.append(c)
                i += 1
                continue
            name, j = m.group(), m.end()
            k = j
            while k < n and text[k] in " \t":
                k += 1
            low = name.lower()
            if k < n and text[k] == "(":
                depth, e = 0, k
                for e in range(k, n):
                    depth += text[e] == "("
                    depth -= text[e] == ")"
                    if depth == 0:
                        break
                inner = text[k + 1:e]
                if low in PROBES:
                    out.append(name + "(" + self._probe(low, inner) + ")")
                    i = e + 1
                    continue
                args = [self.expr(a, behavioral) for a in _split_args(inner)] if inner.strip() else []
                rule = table.get(low, name)
                if rule is _table and not behavioral:
                    raise Untranslatable("table() outside a behavioral source")
                if low == "pwr" and self.src == "ngspice":
                    rule = PWR_NGSPICE[behavioral]
                if self.src == "xyce" and self.ctx.hspice_math and low == "log":
                    rule = name
                if rule is None:
                    raise Untranslatable(f"expression function {low}()")
                if callable(rule):
                    try:
                        out.append(rule(*args))
                    except TypeError:
                        raise Untranslatable(f"expression function {low}() with {len(args)} arguments")
                else:
                    out.append(f"{rule}({', '.join(args)})")
                i = e + 1
                continue
            if self.src == "xyce" and self.tgt == "ngspice" and low in ("temp",):
                out.append("temper")
            elif self.src == "xyce" and low in ("vt", "hertz") and low not in self.ctx.params:
                raise Untranslatable(f"expression variable {low}")
            else:
                out.append(name)
            i = j
        return "".join(out)

    def _probe(self, kind: str, inner: str) -> str:
        """The nodes of v(a, b), the device of i(x): ground names, hierarchy, lead currents."""
        parts = [p.strip() for p in inner.split(",")]
        if kind[0] == "v":
            return ", ".join(self.hier(self.node(p)) for p in parts)
        dev = parts[0].lower()
        if len(parts) > 1 or ":" in dev or "." in dev:
            raise Untranslatable(f"current probe i({inner})")
        if self.tgt == "ngspice" and dev[:1] not in BRANCH_NGSPICE:
            raise Untranslatable(f"current of a {dev[:1].upper()} device in an expression")
        return inner

    def hier(self, name: str) -> str:
        """A node inside a subcircuit: X1:N1 in Xyce, x1.n1 in ngspice."""
        if self.pair == ("xyce", "ngspice"):
            return name.replace(":", ".")
        if self.pair == ("ngspice", "xyce"):
            return name.replace(".", ":")
        return name

    def node(self, name: str) -> str:
        """A node name in the target: the source's ground names become 0, a name that is
        ground only in the target gets a suffix."""
        low = name.lower()
        if low in self.ground(self.src):
            return "0"
        if low in self.ground(self.tgt):
            return name + "_"
        return name

    def ground(self, dialect: str) -> tuple[str, ...]:
        """Ground names besides 0. Xyce's only under .preprocess replaceground."""
        return GROUND[dialect] if dialect != "xyce" or self.ctx.replace_ground else ()

    # -------------------------------------------------------------- statements

    def statements(self, statements: list[Statement], deck: bool) -> list[Statement]:
        out: list[Statement] = []
        end = None
        for k, st in enumerate(statements):
            if deck and k == 0:
                out.append(st)
                continue
            head = st.head
            if end is not None:
                end = None if head == end else end
                continue
            if not head:
                out.append(st)
                continue
            if head in DROP[self.src]:
                end = DROP[self.src][head]
                continue
            if head[0] == "." and head[1:] in NOT_BODY:
                if head == ".control":
                    end = ".endc"
                continue
            out += self.statement(st)
        return out

    def statement(self, st: Statement) -> list[Statement]:
        head = st.head
        if head[0] == ".":
            return self.dot(st)
        if not head[0].isalpha():
            raise Untranslatable(f"statement {st.tokens[0].text!r}")
        letter = head[0]
        if letter in NO_ELEMENT[self.pair]:
            raise Untranslatable(NO_ELEMENT[self.pair][letter])
        self.braces(st)
        if letter == "k":
            return self.mutual(st)
        if letter in "rcl" and self.src == "xyce":
            self.passive(st)
        if letter in "vi":
            self.source(st)
        elif letter == "b" or letter in "eg" and any(w in ("value", "vol", "cur") for w in st.words()):
            self.behavioral(st)
        if letter in NODES or letter == "x":
            self.nodes(st)
        if letter in "dqmjz" and self.tgt == "xyce" and letter in "dqjz" and "m" in st.words():
            raise Untranslatable(f"multiplier m on a {letter.upper()} device (Xyce: R, L, C, M only)")
        return [st]

    # ------------------------------------------------------------- dot commands

    def dot(self, st: Statement) -> list[Statement]:
        w = st.words()
        head = w[0]
        if head in NO_DOT[self.src]:
            raise Untranslatable(NO_DOT[self.src][head])
        rename = DOTS[self.pair].get(head)
        if rename:
            st.set(0, rename)
        if head in (".param", ".global_param", ".func"):
            self.param(st, head)
        elif head == ".model":
            self.model_card(st)
        elif head in (".subckt", ".macro"):
            self.braces(st)
            for i in range(2, len(st.tokens)):
                if i + 1 < len(st.tokens) and st.tokens[i + 1].text == "=" or \
                        w[i] in ("params:", "params", "="):
                    break
                new = self.node(st.tokens[i].text)
                if new == "0":
                    raise Untranslatable(f"ground name {st.tokens[i].text} as a subcircuit port")
                if new != st.tokens[i].text:
                    st.set(i, new)
            if self.pair == ("xyce", "ngspice"):
                self.declare(st, w[1])
        elif head in (".ic", ".nodeset", ".dcvolt"):
            self.braces(st)
            for i, t in enumerate(st.tokens):
                if i > 0 and st.tokens[i - 1].text == "(" and t.text.lower() not in ("(", ")"):
                    new = self.hier(self.node(t.text))
                    if new != t.text:
                        st.set(i, new)
        elif head in OPTION_LINES:
            return self.options(st)
        elif head == ".preprocess":
            if w[1:2] == ["replaceground"]:
                return []
            raise Untranslatable(f".preprocess {' '.join(w[1:2])}")
        elif head in (".lib", ".endl", ".include", ".inc", ".incl", ".ends", ".eom",
                      ".global", ".end"):
            pass
        else:
            raise Untranslatable(f"dot command {head}")
        return [st]

    def options(self, st: Statement) -> list[Statement]:
        """The options that change the circuit, in the target's form; the rest dropped."""
        w = st.words()
        table = OPTION_MAP[self.pair]
        kept = []
        for i in range(1, len(w) - 2):
            if w[i + 1] != "=":
                continue
            key, value = w[i], st.tokens[i + 2].text
            if f"{key}={value.lower()}" in table:
                key = f"{key}={value.lower()}"
            if key not in table:
                continue
            if table[key] is None:
                raise Untranslatable(f"option {key}")
            kept.append(f"{table[key]}={value}")
        if not kept:
            return []
        group = [k.split()[0] for k in kept if " " in k]
        line = ".options " + (group[0] + " " if group else "") + \
            " ".join(k.split()[-1] for k in kept) + "\n"
        toks, tail = tokenize(line, COMMENT[self.tgt])
        return [Statement(line, toks, tail)]

    def declare(self, st: Statement, sub: str) -> None:
        """Xyce takes X line parameters a subcircuit does not declare (Reference Guide
        2.1.37), and they override a .param inside it; ngspice takes declared ones only.
        A parameter only passed is declared, with the global of its name as default."""
        extra = self.ctx.passed.get(sub, set()) - self.ctx.declared.get(sub, set())
        if extra & self.ctx.inner.get(sub, set()):
            raise Untranslatable("X line parameter overrides a .param inside the subcircuit")
        for name in sorted(extra):
            default = "{" + name + "}" if name in self.ctx.globals else "0"
            st.tokens += [Token(" ", name), Token("", "="), Token("", default)]
            st.edited = True

    def param(self, st: Statement, head: str) -> None:
        """Parameters and functions: their right-hand sides as expressions, written with
        braces or without."""
        w = st.words()
        if self.src == "xyce" and head != ".func" and \
                re.search(r"\b(time|freq|hertz)\b|\b[vi]\s*\(", " ".join(w[1:])):
            raise Untranslatable(f"time-dependent {head}")
        if head == ".func":
            close = next((i for i in range(2, len(w)) if w[i] == ")"), None)
            if close is None:
                raise Untranslatable(".func without arguments")
            start = close + 2 if close + 1 < len(w) and w[close + 1] == "=" else close + 1
            ranges = [(start, len(w))]
        else:
            names = [i for i in range(1, len(w) - 1) if w[i + 1] == "=" and _depth(w[1:i]) == 0]
            ranges = [(i + 2, names[k + 1] if k + 1 < len(names) else len(w))
                      for k, i in enumerate(names)]
        for start, end in reversed(ranges):
            if start >= end:
                continue
            toks = st.tokens[start:end]
            text = "".join(t.ws + t.text for t in toks)[len(toks[0].ws):]
            braced = len(toks) == 1 and text[:1] in "{'"
            body = text[1:-1] if braced else text
            new = self.expr(body, behavioral=False)
            quote = braced and text[0] == "'" and self.tgt == "xyce"
            if new != body or quote:
                new = "{" + new + "}" if braced else new
                st.tokens[start:end] = [Token(toks[0].ws, new)]
                st.edited = True

    # ------------------------------------------------------------------ models

    def model_card(self, st: Statement) -> None:
        w = st.words()
        if len(w) < 3:
            return
        if w[2] == "ako" or w[2].startswith("ako:"):
            raise Untranslatable("model inheritance (ako)")
        typ = w[2]
        self.braces(st)
        key = PASSIVE_VALUE.get(typ)
        if key:
            k = next((i for i in range(3, len(w) - 2) if w[i] in key and w[i + 1] == "="), None)
            if k is not None and self.src == "ngspice":
                raise Untranslatable(f"{typ} model parameter {w[k]} (a value in ngspice, "
                                     f"a multiplier in Xyce)")
            if k is not None:                   # moved onto the instances, see passive()
                ws = st.tokens[k].ws
                del st.tokens[k:k + 3]
                if k < len(st.tokens):
                    st.tokens[k].ws = st.tokens[k].ws or ws
                st.edited = True
        if typ in FAMILY_OF_TYPE:
            self.level(st, FAMILY_OF_TYPE[typ])
            return
        if typ in TYPES[self.tgt]:
            return
        new = TYPE_NAMES.get(self.pair, {}).get(typ)
        if new:
            st.set(2, new)
            return
        raise Untranslatable(f"model type {typ}")

    def level(self, st: Statement, family: str) -> None:
        w = st.words()
        k = next((i for i in range(3, len(w) - 2) if w[i] == "level" and w[i + 1] == "="), None)
        if k is not None and not (re.fullmatch(r"[\d.e+-]+", w[k + 2]) and
                                  number(w[k + 2]) == int(number(w[k + 2]))):
            raise Untranslatable(f"model level {st.tokens[k + 2].text}")
        lvl = int(number(w[k + 2])) if k is not None else 1
        model = LEVELS[self.src].get((family, lvl))
        if model is None:
            raise Untranslatable(f"{family} level {lvl} of {self.src}")
        target = [l for (f, l), m in LEVELS[self.tgt].items() if f == family and m == model]
        if not target:
            raise Untranslatable(f"{model} ({family} level {lvl}) has no {self.tgt} model")
        new = lvl if lvl in target else target[0]
        if new != lvl:
            if k is None:
                _add_param(st, "level", str(new))
            else:
                st.set(k + 2, str(new))
        self.version(st, model)

    def version(self, st: Statement, model: str) -> None:
        src, tgt = VERSIONS.get((self.src, model)), VERSIONS.get((self.tgt, model))
        if not src:
            return
        w = st.words()
        k = next((i for i in range(3, len(w) - 2) if w[i] == "version" and w[i + 1] == "="), None)
        given = _version(st.tokens[k + 2].text) if k is not None else None
        computed = src(given)
        text = ".".join(map(str, computed))
        if tgt(computed)[:2] != computed[:2]:
            raise Untranslatable(f"{model} {text} of {self.src}: {self.tgt} computes "
                                 f"{'.'.join(map(str, tgt(computed)))}")
        if k is None:
            _add_param(st, "version", text)
        elif st.tokens[k + 2].text != text:
            st.set(k + 2, text)

    # ---------------------------------------------------------------- elements

    def value_positions(self, st: Statement) -> list[int]:
        """Indices of the positional values of an element: what follows its terminals and
        model, outside of any function's parentheses."""
        w = st.words()
        letter = w[0][0]
        if letter not in NODES:
            return []
        first = 1 + NODES[letter]
        if letter in "qm":                      # optional terminals before the model
            first = next((i + 1 for i in range(first, len(w)) if self.model(w[i])), None)
            if first is None:
                return []
        elif letter in "dzj":
            first += 1
        elif letter in "fh":
            first += 1                          # the controlling source
        elif letter in "rcl" and first < len(w) and self.model(w[first]):
            first += 1
        if letter in "efgh" and "poly" in w:          # controlling nodes or sources follow
            return []
        # Source function arguments are values; other parentheses hold names.
        inside = letter in "vi"
        out, depth = [], 0
        for i in range(first, len(w)):
            if w[i] == "(":
                depth += 1
            elif w[i] == ")":
                depth -= 1
            elif (depth == 0 or inside) and w[i] not in ("=", ",") and \
                    not (i + 1 < len(w) and w[i + 1] in ("=", "(")) and w[i - 1] != "=":
                out.append(i)
        return out

    def braces(self, st: Statement) -> None:
        """Expressions in braces translated; in ngspice a parameter is only substituted in
        braces, Xyce substitutes a bare name in a value position too."""
        w = st.words()
        behavioral = st.head[0] == "b" or any(x in ("value", "vol", "cur") for x in w)
        for i, t in enumerate(st.tokens):
            if t.text[:1] == "{" or (t.text[:1] == "'" and len(t.text) > 1):
                body = t.text[1:-1]
                new = self.expr(body, behavioral or bool(re.search(r"\b[vi]\s*\(", body, re.I)))
                if new != body or t.text[0] == "'" and self.tgt == "xyce":
                    st.set(i, "{" + new + "}")
        if self.tgt != "ngspice":
            return
        positions = set(self.value_positions(st)) if st.head[0] != "." else set()
        for i, t in enumerate(st.tokens):
            if (i in positions or i > 1 and st.tokens[i - 1].text == "=") and \
                    t.text.lower() in self.ctx.params and not is_number(t.text):
                st.set(i, "{" + t.text + "}")

    def nodes(self, st: Statement) -> None:
        w = st.words()
        letter = w[0][0]
        if letter == "x":
            span = range(1, _subckt_of(w)[1])
        elif letter in "qm":                    # terminals up to the model
            model = next((i for i in range(1 + NODES[letter], len(w)) if self.model(w[i])),
                         1 + NODES[letter])
            span = range(1, model)
        else:
            span = range(1, min(1 + NODES[letter], len(w)))
        for i in span:
            new = self.node(st.tokens[i].text)
            if new != st.tokens[i].text:
                st.set(i, new)

    def mutual(self, st: Statement) -> list[Statement]:
        """K couples every pair of the inductors it lists with one coefficient (Xyce);
        ngspice couples two per K line."""
        w = st.words()
        names = [t.text for t in st.tokens[1:] if t.text.lower()[:1] == "l" and
                 not is_number(t.text) and t.text.lower() not in self.ctx.params]
        rest = st.tokens[1 + len(names):]
        if any(self.model(t.text) for t in rest):
            raise Untranslatable("nonlinear mutual inductor (core model)")
        if self.tgt == "ngspice" and len(rest) == 1 and rest[0].text.lower() in self.ctx.params:
            st.set(1 + len(names), "{" + rest[0].text + "}")
        if len(names) <= 2 or self.tgt == "xyce":
            return [st]
        coupling = "".join(t.ws + t.text for t in rest).strip()
        name = st.tokens[0].text
        out = []
        for n, (a, b) in enumerate(combinations(names, 2)):
            raw = f"{name}{'' if n == 0 else f'_{n}'} {a} {b} {coupling}\n"
            toks, tail = tokenize(raw, COMMENT[self.tgt])
            out.append(Statement(raw, toks, tail))
        return out

    def source(self, st: Statement) -> None:
        w = st.words()
        for i in range(3, len(w)):
            if w[i] not in SOURCE_FUNCTIONS[self.src] or i + 1 < len(w) and w[i + 1] == "=":
                continue
            new = SOURCE_NAMES.get(self.pair, {}).get(w[i], w[i])
            if new not in SOURCE_FUNCTIONS[self.tgt]:
                raise Untranslatable(f"{w[i]} source")
            if new != w[i]:
                st.set(i, new)
            if new == "pwl" and self.tgt == "ngspice":
                self.pwl(st, i)
            if new == "pulse" and self.src == "xyce":
                # A zero rise or fall time is zero in Xyce, the time step in ngspice
                # (Xyce Reference Guide table 6-1, ngspice vsrcload.c).
                args = [x for x in w[i + 1:] if x not in ("(", ")", ",")]
                if any(is_number(a) and number(a) == 0 for a in args[3:5]):
                    raise Untranslatable("pulse with zero rise or fall time")
            break
        if self.tgt == "xyce":
            # Xyce reads DC and AC followed by their values, not as assignments.
            for i in range(len(w) - 1, 2, -1):
                if w[i] in ("dc", "ac") and i + 2 < len(w) and w[i + 1] == "=":
                    del st.tokens[i + 1]
                    st.tokens[i + 1].ws = st.tokens[i + 1].ws or " "
                    st.edited = True

    def passive(self, st: Statement) -> None:
        """The multiplier of a Xyce R, C or L model moved onto the instance value."""
        w = st.words()
        if len(w) < 4 or not self.ctx.multiplier.get(w[3]):
            return
        m = self.ctx.multiplier[w[3]]
        k = next((i for i in range(4, len(w)) if w[i] == w[0][0] and w[i - 1] != "=" and
                  i + 1 < len(w) and w[i + 1] == "="), None)
        k = k + 2 if k is not None else 4 if len(w) > 4 and w[4] not in ("=",) and \
            (len(w) == 5 or w[5] != "=") else None
        if k is None:
            raise Untranslatable(f"Xyce {w[0][0].upper()} model multiplier without an instance value")
        v = st.tokens[k].text
        st.set(k, "{(" + (v[1:-1] if v[:1] == "{" else v) + ")*(" + m.strip("{}") + ")}")

    def pwl(self, st: Statement, at: int) -> None:
        """Xyce PWL [FILE name] [pairs] [TD=] [R=], parentheses optional; ngspice reads
        pwl(pairs) r= td= with the same meaning of r and td, on voltage sources only."""
        w = st.words()
        points, keys, k = [], {}, at + 1
        while k < len(w):
            if w[k] in ("(", ")", ","):
                k += 1
            elif w[k] in ("r", "td") and k + 2 < len(w) and w[k + 1] == "=":
                keys[w[k]] = st.tokens[k + 2].text
                k += 3
            elif w[k] == "file" and k + 1 < len(w):
                path = self.file.parent / st.tokens[k + 1].text.strip("\"'")
                try:
                    data = path.read_text(encoding="latin-1")
                except OSError:
                    raise Untranslatable(f"PWL file {st.tokens[k + 1].text} not found")
                points += re.split(r"[\s,]+", data.strip())
                k += 2
            elif w[k + 1:k + 2] == ["="]:
                raise Untranslatable(f"PWL source parameter {w[k]}")
            else:
                points.append(st.tokens[k].text)
                k += 1
        if not keys and "file" not in w[at + 1:]:
            return
        if keys and w[0][0] == "i":
            raise Untranslatable("PWL current source with R or TD (ngspice: voltage sources only)")
        text = "pwl(" + " ".join(points) + ")" + "".join(f" {k}={v}" for k, v in keys.items())
        st.tokens[at:] = [Token(st.tokens[at].ws, text)]
        st.edited = True

    def behavioral(self, st: Statement) -> None:
        """B, and E/G with an expression: Xyce wants the expression in braces, ngspice
        reads it with or without."""
        if self.tgt != "xyce":
            return
        w = st.words()
        for i in range(len(w) - 2):
            if w[i] in ("v", "i", "value", "vol", "cur") and w[i + 1] == "=":
                if w[i] in ("vol", "cur"):
                    st.set(i, "value")
                if st.tokens[i + 2].text[:1] == "{":
                    return
                end = next((j for j in range(i + 3, len(w) - 1) if w[j + 1] == "=" and
                            _depth(w[i + 2:j]) == 0), len(w))
                text = "".join(t.ws + t.text for t in st.tokens[i + 2:end]).strip()
                text = self.expr(text, behavioral=True)
                st.tokens[i + 2:end] = [Token(st.tokens[i + 2].ws, "{" + text + "}")]
                st.edited = True
                return


def _subckt_of(w: list[str]) -> tuple[str, int]:
    """The subcircuit an X line instantiates and its index: the last name before the
    parameters."""
    k = next((i for i in range(1, len(w)) if w[i] in ("params:", "params") or
              i + 1 < len(w) and w[i + 1] == "="), len(w)) - 1
    return w[k], k


def _add_param(st: Statement, name: str, value: str) -> None:
    """``name=value`` at the end of a model card, inside its parentheses if it has them."""
    at = len(st.tokens) - 1 if st.tokens[-1].text == ")" else len(st.tokens)
    st.tokens[at:at] = [Token(" ", name), Token("", "="), Token("", value)]
    st.edited = True


def _depth(words: list[str]) -> int:
    return sum(w == "(" for w in words) - sum(w == ")" for w in words)


def _version(text: str) -> tuple[int, int, int]:
    """'4.8.2', '4.82', '4.8', 4.8 -> (4, 8, 2), (4, 8, 2), (4, 8, 0), (4, 8, 0)."""
    t = text.strip("'\"{}")
    parts = t.split(".")
    if len(parts) == 2 and len(parts[1]) == 2 and parts[1].isdigit():
        parts = [parts[0], parts[1][0], parts[1][1]]
    try:
        nums = [int(p) for p in parts[:3]]
    except ValueError:
        raise Untranslatable(f"model version {text}")
    return tuple(nums + [0] * (3 - len(nums)))


# ------------------------------------------------------------------------ files

def translate_text(texts: dict[Path, tuple[str, bool]], source: str, target: str
                   ) -> dict[Path, str]:
    """Each file's text in the target dialect. ``texts``: path -> (text, is the deck). A
    file whose statements need no change keeps its text."""
    tr = Translator(source, target)
    parsed = {p: parse(t, source, deck) for p, (t, deck) in texts.items()}
    for sts in parsed.values():
        tr.read_context(sts)
    marks = COMMENT[tr.tgt]
    out = {}
    for p, sts in parsed.items():
        tr.file = p
        new = tr.statements(sts, texts[p][1])
        out[p] = "".join(st.render(marks) for st in new)
    return out


def translate(case: Case, nl: Netlist, dest: Path, target: str) -> list[Path]:
    """Rewrite the body of ``nl`` staged under ``dest`` in place into ``target``: the deck
    and every netlist it reaches; a library file only where it needs a change. The files
    changed."""
    g = case.graphs[nl.file]
    files = [staged(dest, f) for f in sorted(g.files) if f.suffix.lower() not in VA_SUFFIXES]
    if any(f.suffix.lower() == ".gz" for f in files):
        raise Untranslatable("compressed netlist file")
    deck = staged(dest, case.directory / nl.file)
    texts = {p: (p.read_bytes().decode("latin-1"), p == deck) for p in files}
    out = translate_text(texts, nl.dialect, target)
    changed = []
    for p, text in out.items():
        if text != texts[p][0]:
            p.write_bytes(text.encode("latin-1"))
            changed.append(p)
    return changed
