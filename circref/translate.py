"""A circuit body from one SPICE dialect into another.

A staged body (the top-level deck and the files it includes) is rewritten in place. Each
file is read into statements: continuation lines joined, comments kept, every token with
the text in front of it, so that a statement no rule touches is written back byte for
byte. The rules of the dialect pair are applied statement by statement; what the target
has no equivalent for raises Untranslatable, naming the construct.

ngspice is the hub: the pairs in PAIRS have rules of their own, any other pair goes
through ngspice (Xyce to WRspice is Xyce to ngspice, then ngspice to WRspice), so that
each difference of a dialect is stated once, against ngspice.

Where a difference is a mapping it is data below: model levels and versions per device,
model types, expression functions, source forms, comment marks, ground names. Every entry
is taken from the simulators' documentation and source: Xyce Reference Guide 7.9 and Xyce
7.10 (``registerDevice``, ``ExpressionLexer.l``, ``ExpressionParser.yxx``,
``N_DEV_SourceData.C``), ngspice manual and ngspice 47 (``inpdomod.c``, ``inpptree.c``,
``ptfuncs.c``, ``numparam/xpressn.c``, ``inpcom.c``), WRspice 4.3.24 (xictools: the help
text ``xt_base/sphelp/spInput.hlp``, ``spSources.hlp``, ``spExpressions.hlp``; device keys,
levels and model names in ``wrspice/devlib/*/*.cc``; ``src/inp/inpfuncs.cc`` and
``inpptree.cc`` for device expressions, ``src/fte/parser.cc`` and ``cmath1.cc`` for
parameter expressions, ``src/fte/subexpand.cc`` for subcircuit parameters).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

from . import netlist
from .adapters import NOT_BODY, Ngspice
from .circuit import Unsupported, number
from .entry import Case, Netlist
from .stage import staged


class Untranslatable(Exception):
    """A construct of the source dialect without an equivalent in the target dialect."""


# Dialects read with the rules of another: SPICE3 decks are ngspice decks.
FAMILY = {"ngspice": "ngspice", "spice3": "ngspice", "xyce": "xyce", "wrspice": "wrspice",
          "spicesharp": "spicesharp"}
# The dialect pairs with rules; every other pair goes through the hub.
HUB = "ngspice"
PAIRS = {("xyce", "ngspice"), ("ngspice", "xyce"), ("ngspice", "wrspice"), ("ngspice", "spicesharp")}

# Inline comment marks a dialect reads, and the one written in the target. ngspice: ``;``
# anywhere, ``$`` after a blank or comma, ``//`` (inp_stripcomments_line); Xyce: ``;`` only
# (SpiceSeparatedFieldTool). WRspice: ``$`` or ``;`` between blanks only (spInput.hlp,
# Comments). SpiceSharpParser: ``$`` and ``;`` where a token starts, ``;`` inside a word
# is part of it, no ``//`` (SpiceLexer.cs). None is recognized for those two here, so that
# every mark is written isolated.
COMMENT = {"ngspice": (";", "$", "//"), "xyce": (";",), "wrspice": (), "spicesharp": ()}
COMMENT_MARK = {"ngspice": ";", "xyce": ";", "wrspice": " $ ", "spicesharp": " $ "}
# Comment lines a dialect executes: in WRspice ``*@`` and ``*#`` lines are .exec and
# .control statements (spInput.hlp, Comments).
EXECUTED_COMMENTS = {"wrspice": ("*@", "*#")}

# Node names that are ground besides 0. ngspice: ``gnd`` (inp_fix_gnd_name). Xyce: GND,
# GND! and GROUND, but only under ``.preprocess replaceground true``. WRspice: only 0
# (spInput.hlp, Input Format); SpiceSharp: only 0 (Constants.cs).
GROUND = {"ngspice": ("gnd",), "xyce": ("gnd", "gnd!", "ground"), "wrspice": (), "spicesharp": ()}

# A node inside a subcircuit: the separator, and whether the name starts at the top
# instance (Xyce X1:N1, ngspice x1.n1, SpiceSharpParser x1.n1 with its default separator)
# or at the node (WRspice n1.x1, subexpand.cc and spInput.hlp, Subcircuit Expansion).
HIER = {"xyce": (":", True), "ngspice": (".", True), "wrspice": (".", False),
        "spicesharp": (".", True)}

# How an expression is delimited where the target evaluates it when reading: braces in
# ngspice, Xyce and SpiceSharpParser, single quotes in WRspice, which has no braces
# (spInput.hlp, Single-Quoted Expressions).
QUOTE = {"ngspice": ("{", "}"), "xyce": ("{", "}"), "wrspice": ("'", "'"), "spicesharp": ("{", "}")}
# The delimiters a dialect reads: ngspice takes single quotes as braces (inpcom.c), Xyce
# braces only, SpiceSharpParser single quotes only after = (SpiceLexer.cs).
READ_QUOTES = {"ngspice": "{'", "xyce": "{", "wrspice": "'", "spicesharp": "{"}
# Dialects that read a .param value as one token unless it is quoted (WRspice:
# spInput.hlp, .param Line).
ONE_TOKEN_VALUES = {"wrspice"}

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
    # WRspice: dv_levels of each device in devlib (the readme.moslevel table is older).
    # Its VBIC is ngspice's of release 17 (vbic.cc), its MESFET the Statz model of SPICE3,
    # JFET level 2 SPICE3's Parker-Skellern model (jfet2). The diode accepts level 3 but
    # computes the SPICE3 diode (dio.cc has no level), so only level 1 is the same model.
    "wrspice": {
        ("mos", 1): "mos1", ("mos", 2): "mos2", ("mos", 3): "mos3", ("mos", 6): "mos6",
        ("mos", 9): "bsim3", ("mos", 53): "bsim3",
        ("mos", 12): "bsim4", ("mos", 13): "bsim4", ("mos", 14): "bsim4", ("mos", 15): "bsim4",
        ("mos", 54): "bsim4", ("mos", 16): "bsim4", ("mos", 56): "bsim4", ("mos", 17): "bsim4",
        ("mos", 59): "bsim4", ("mos", 18): "bsim4", ("mos", 60): "bsim4",
        ("mos", 24): "BSIMSOI 4.4", ("mos", 71): "BSIMSOI 4.4",
        ("bjt", 1): "gummel-poon", ("bjt", 4): "VBIC 1.2",
        ("diode", 1): "diode",
        ("jfet", 1): "jfet", ("jfet", 2): "Parker-Skellern JFET",
        ("mesfet", 1): "statz",
        ("r", 1): "resistor",
    },
    # SpiceSharp 3.2.3: Mosfet1/2/3 (MosfetModelGenerator.cs), and one model each for the
    # BJT (Gummel-Poon), diode, JFET and resistor, ports of SPICE3's.
    "spicesharp": {
        ("mos", 1): "mos1", ("mos", 2): "mos2", ("mos", 3): "mos3",
        ("bjt", 1): "gummel-poon", ("diode", 1): "diode", ("jfet", 1): "jfet",
        ("r", 1): "resistor",
    },
}
# Families whose models in the target have no level parameter: one model, and level= on
# its card is an unknown parameter (SpiceSharp's BJT, diode, JFET and resistor models).
NO_LEVEL = {"spicesharp": {"bjt", "diode", "jfet", "r"}}

# Models whose version the target selects by level rather than by a version parameter:
# version -> level; a version takes the level of its major and minor version with the
# nearest patch. WRspice BSIM4 (devlib/bsim4.*/b4.cc).
LEVEL_OF_VERSION = {
    ("wrspice", "bsim4"): {(4, 2, 1): 12, (4, 3, 0): 13, (4, 4, 0): 14, (4, 6, 5): 15,
                           (4, 7, 0): 16, (4, 8, 0): 17, (4, 8, 2): 18},
}

# Model types each dialect knows, besides FAMILY_OF_TYPE, and the ones that are spelled
# differently. ngspice: inpdomod.c; Xyce: registerModelType; WRspice: the model names of
# each device in devlib.
TYPES = {
    "xyce": {"c", "cap", "l", "ind", "ltra", "vswitch", "iswitch", "switch", "core", "zod",
             "dig", "transline", "memristor", "pde", "rom", "lin", "opamp", "adc", "dac",
             "neuron", "neuronpop", "synapse", "rxn", "min", "mil", "delay", "genext", "ext",
             "battery"},
    "ngspice": {"c", "l", "ltra", "sw", "csw", "urc", "txl", "cpl", "vdmos", "vdmosn", "vdmosp",
                "nsoi", "psoi", "numd", "nbjt", "numos", "nhfet", "phfet"},
    "wrspice": {"c", "l", "ltra", "tra", "sw", "csw", "urc"},
    # SpiceSharpParser: SpiceObjectMappings.cs, models.
    "spicesharp": {"c", "sw", "csw", "vswitch", "iswitch"},
}
TYPE_NAMES = {("xyce", "ngspice"): {"cap": "c", "ind": "l"}, ("ngspice", "wrspice"): {"res": "r"}}

# Model flags written without a value, by model type: the target's flag (set to 1), or
# None for a setting of the solver only. ngspice LTRA (ltra.c): steplimit, nosteplimit,
# lininterp, quadinterp, mixedinterp, truncnr, truncdontcut, nocontrol (no time step
# control); Xyce LTRA (N_DEV_LTRA.C) has all but nocontrol as parameters. WRspice's
# lossy line (tra.cc, an algorithm of its own) has lininterp, quadinterp, truncnr and
# truncdontcut; the others set the step control of ngspice's.
FLAGS = {("ngspice", "xyce"): {"ltra": {f: f for f in (
    "steplimit", "nosteplimit", "lininterp", "quadinterp", "mixedinterp", "truncnr",
    "truncdontcut")} | {"nocontrol": None}},
         ("ngspice", "wrspice"): {"ltra": {f: f for f in (
             "lininterp", "quadinterp", "truncnr", "truncdontcut")} | {
             f: None for f in ("steplimit", "nosteplimit", "mixedinterp", "nocontrol")}}}

# Instance parameters of the source dialect the target's element does not have.
# ngspice B: tc1, tc2 scale the output with temperature; ngspice R: ac is a resistance
# for AC analysis only (ngspice manual, resistor and B source). Xyce's B and R have
# neither, nor WRspice's A source and R (src.cc, res.cc).
_NGSPICE_ONLY = {
    "b": {"tc1": "temperature coefficient of a B source",
          "tc2": "temperature coefficient of a B source"},
    "r": {"ac": "AC-only resistance"}}
NO_INSTANCE_PARAMS = {("ngspice", "xyce"): _NGSPICE_ONLY, ("ngspice", "wrspice"): _NGSPICE_ONLY,
                      # SpiceSharp: Resistors/Inductors/Parameters.cs; a resistor takes
                      # temperature coefficients as tc=a,b only (RLCKGenerator.cs).
                      ("ngspice", "spicesharp"): _NGSPICE_ONLY | {
                          "r": {"ac": "AC-only resistance", "tc1": "SpiceSharp reads tc=a,b",
                                "tc2": "SpiceSharp reads tc=a,b"},
                          "l": {p: "temperature dependence of an inductor"
                                for p in ("temp", "dtemp", "tc1", "tc2")}}}

# Elements keyed by another letter in the target: the letter put in front of the name.
# WRspice keys SPICE3's B source by A, B is its Josephson junction (spSources.hlp, General
# I and V Sources).
LETTERS = {("ngspice", "wrspice"): {"b": "a"}}

# What does not take the multiplier m: element letters and models. Xyce: R, L, C, M only
# (Reference Guide 2.3); WRspice: the devices with an m parameter in devlib (R, C, L,
# diode, MOS levels 1-6, BSIM4 from 4.6.5, VBIC), and no subcircuit call: subexpand.cc
# passes m on as a parameter.
#   SpiceSharpParser element forms that differ from ngspice's:
#   a 3-terminal Q ties the substrate to the emitter (BipolarJunctionTransistorGenerator.cs);
EMITTER_SUBSTRATE = {"spicesharp"}
#   a C with a model needs l= (RLCKGenerator.GenerateCap);
CAPACITOR_MODEL_GEOMETRY = {"spicesharp"}
#   K finds its inductors by the name as written, outside any subcircuit (GenerateMut);
GLOBAL_COUPLING = {"spicesharp"}
#   an X line parameter is evaluated in the subcircuit's scope (EvaluationContext.cs);
CALLEE_SCOPE = {"spicesharp"}
#   dot commands, library sections and .ends names are compared case-sensitively;
CASE_SENSITIVE_NAMES = {"spicesharp"}
#   a V or I takes one expression in braces (VoltageSourceGenerator.cs .Single);
ONE_EXPRESSION = {"spicesharp"}
#   a tab inside an expression is an unknown token (Lexers/Expressions/Lexer.cs).
NO_TABS = {"spicesharp"}

NO_MULTIPLIER = {"xyce": {"d", "q", "j", "z"},
                 "wrspice": {"x", "j", "z", "gummel-poon", "bsim3", "BSIMSOI 4.4"},
                 # SpiceSharpParser: V has none, a linear E, F, G or H with m is dropped
                 # without an error (VoltageSourceGenerator.cs, CurrentSourceGenerator.cs).
                 "spicesharp": {"v", "e", "f", "g", "h"}}

# Verilog-A modules (ngspice loads them as OSDI, N instances) that are built into Xyce:
# module -> (device letter, model types for type=+1/-1, level, version Xyce implements).
# The version is read from the module's source; another version is not translated.
# Xyce Reference Guide 2.3.20.12: PSP 103.4, levels 103 and 1031 (self-heating).
VA_BUILTIN = {
    "xyce": {"psp103va": ("m", ("nmos", "pmos"), 103, "103.4"),
             "psp103tva": ("m", ("nmos", "pmos"), 1031, "103.4")},
}

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
    # WRspice BSIM3 is 3.3.0 (devlib/bsim3.3.0); its BSIM4 versions are levels.
    ("wrspice", "bsim3"): lambda v: (3, 3, 0),
}

# Expression functions with another name or form in the target. A string is the target
# name, a callable builds the target text from the translated arguments, None has no
# equivalent; a dict holds the rule in behavioral expressions (True) and in parameter
# expressions (False). Forms into ngspice are chosen so that they hold in both of its
# expression parsers (numparam for parameters, inpptree for behavioral sources).
#   Xyce: log is log10, pwr and pow are pow, pwrs is the signed power, stp(x) is x > 0,
#   if(c, a, b), limit(x, lo, hi), sign(x, y) is |x| with the sign of y, int truncates.
#   ngspice: log and ln are ln, pwr is the signed power in inpptree and |x|^y in numparam,
#   pow and ^ are x^y (0 at x = 0), u(x) is 1, 0.5, 0 for x > 0, x = 0, x < 0 (PTustep),
#   ternary_fcn(c, a, b), limit(nom, var) is random, int truncates, nint rounds half to even.
#   WRspice: behavioral (device) expressions have the functions of inpfuncs.cc PTfuncs
#   only: no min, max, floor, ceil, int, no ternary operator (inpptree.cc bad_ops); their
#   relational operators give 1 or 0 with a zero derivative. Parameter expressions are
#   vector expressions (parser.cc ft_funcs): no min or max; pow(x, y) truncates y to an
#   integer, ^ does not, pwr is the signed power, int rounds half to even (cmath1.cc).
#   SpiceSharp: parameters and behavioral sources share SpiceSharpBehavioral 3.2.0's
#   functions (RealBuilderHelper.Defaults, found before the parser's own in
#   CustomRealBuilder.cs): pwr is |x|^y, pwrs the signed power, u, u2, uramp, nint as in
#   ngspice, limit(x, lo, hi) clamps; int truncates (IntFunction.cs); a condition is
#   true above 0.5 (RealBuilder.cs).
def _ternary(c, a, b):
    return f"(({c}) ? ({a}) : ({b}))"


def _select(c, a, b):
    """``c ? a : b`` from relational operators, for WRspice's device expressions."""
    return f"((({c}) != 0)*({a}) + (({c}) == 0)*({b}))"


def _selects(text: str) -> str:
    """Every ternary operator in ``text`` as a selection with relational operators: in
    each argument of a parenthesized group the first ``?`` at its depth splits it,
    right-associative."""
    if "?" not in text:
        return text
    out, i = [], 0
    while i < len(text):
        if text[i] == "(":
            j = _close(text, i)
            out.append("(" + ", ".join(_selects(a) for a in _split_args(text[i + 1:j - 1])) + ")")
            i = j
        else:
            out.append(text[i])
            i += 1
    flat = "".join(out)
    depth, q = 0, None
    for k, ch in enumerate(flat):
        depth += ch == "("
        depth -= ch == ")"
        if ch == "?" and depth == 0:
            q = k
            break
    if q is None:
        return flat
    depth, nested = 0, 0
    for k in range(q + 1, len(flat)):
        ch = flat[k]
        depth += ch == "("
        depth -= ch == ")"
        if depth == 0 and ch == "?":
            nested += 1
        elif depth == 0 and ch == ":":
            if nested:
                nested -= 1
            else:
                return _select(flat[:q].strip(), flat[q + 1:k].strip(), _selects(flat[k + 1:].strip()))
    raise Untranslatable(f"ternary without ':' in {text}")


def _operand_start(s: str, i: int) -> int:
    """Where the operand that ends before ``i`` starts: a group or call, a name or a number."""
    j = i
    while j > 0 and s[j - 1] in " \t":
        j -= 1
    if j and s[j - 1] == ")":
        depth = 0
        for j in range(j - 1, -1, -1):
            depth += s[j] == ")"
            depth -= s[j] == "("
            if depth == 0:
                break
    while j and (s[j - 1].isalnum() or s[j - 1] in "_."
                 or s[j - 1] in "+-" and j > 2 and s[j - 2] in "eE" and s[j - 3].isdigit()):
        j -= 1
    return j


def _operand_end(s: str, i: int) -> int:
    """Where the operand that starts at ``i`` ends: a sign, then a group, a call, a name or
    a number."""
    j = i
    while j < len(s) and s[j] in " \t":
        j += 1
    if j < len(s) and s[j] in "+-":
        j += 1
    while j < len(s) and (s[j].isalnum() or s[j] in "_."
                          or s[j] in "+-" and s[j - 1] in "eE" and j > 1 and s[j - 2].isdigit()):
        j += 1
    if j < len(s) and s[j] == "(":
        j = _close(s, j)
    return j


def _powers(text: str, rule) -> str:
    """Every power operator (``^``, ``**``) in ``text`` written by ``rule(base, exponent)``,
    the rightmost first (right-associative)."""
    text = text.replace("**", "^")
    while "^" in text:
        k = text.rindex("^")
        a, b = _operand_start(text, k), _operand_end(text, k + 1)
        text = text[:a] + rule(text[a:k].strip(), text[k + 1:b].strip()).replace("^", "\0") + text[b:]
    return text.replace("\0", "^")


def _min(a, b):
    return f"((({a})+({b})-abs(({a})-({b})))/2)"


def _max(a, b):
    return f"((({a})+({b})+abs(({a})-({b})))/2)"


def _uramp(x):
    return f"((({x})+abs({x}))/2)"


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
        "table": {True: _table, False: None},
        "sign": lambda x, y: _ternary(f"{y}) >= (0", f"abs({x})", f"-abs({x})"),
        "int": lambda x: _ternary(f"{x}) >= (0", f"floor({x})", f"ceil({x})"),
        "arctan": "atan",
        # Without a UQ analysis Xyce's random functions return their mean (Reference
        # Guide, table 2-33 note 1); ngspice draws a random number.
        "agauss": lambda mu, *_: mu, "gauss": lambda mu, *_: mu, "aunif": lambda mu, *_: mu,
        "unif": lambda mu, *_: mu, "rand": lambda: "0.5",
        "atan2": None, "fmod": None, "sdt": None, "ddx": None, "fasttable": None,
        "spline": None, "akima": None, "cubic": None, "wodicka": None, "bli": None,
        "tablefile": None, "schedule": None, "poly": None, "splinefile": None,
        "akimafile": None, "cubicfile": None, "wodickafile": None, "blifile": None,
        "fasttablefile": None, "spice_pulse": None, "spice_sin": None, "spice_exp": None,
        "spice_sffm": None,
    },
    ("ngspice", "wrspice"): {
        "pow": lambda x, y: f"(({x})^({y}))",
        "pwr": {True: lambda x, y: f"(sgn({x})*abs({x})^({y}))",
                False: lambda x, y: f"(abs({x})^({y}))"},
        "ternary_fcn": {True: _select, False: _ternary},
        "min": _min, "max": _max,
        "u": lambda x: f"(0.5*(sgn({x})+1))",
        "uramp": _uramp,
        "u2": lambda x: f"({_uramp(x)}-{_uramp(f'({x})-1')})",
        "sqr": lambda x: f"(({x})*({x}))",
        "eq0": lambda x: f"(({x}) == 0)", "ne0": lambda x: f"(({x}) != 0)",
        "gt0": lambda x: f"(({x}) > 0)", "lt0": lambda x: f"(({x}) < 0)",
        "ge0": lambda x: f"(({x}) >= 0)", "le0": lambda x: f"(({x}) <= 0)",
        "int": {True: None, False: lambda x: f"(sgn({x})*floor(abs({x})))"},
        "nint": {True: None, False: "int"},
        "floor": {True: None, False: "floor"}, "ceil": {True: None, False: "ceil"},
        "arctan": "atan",
        "pwl": None, "pwl_derivative": None, "ddt": None, "vec": None, "var": None,
    },
    ("ngspice", "spicesharp"): {
        "pwr": {True: "pwrs", False: "pwr"},
        "ternary_fcn": lambda c, a, b: _ternary(f"({c}) != 0", a, b),
        "sqr": lambda x: f"(({x})*({x}))",
        "eq0": lambda x: f"(({x}) == 0)", "ne0": lambda x: f"(({x}) != 0)",
        "gt0": lambda x: f"(({x}) > 0)", "lt0": lambda x: f"(({x}) < 0)",
        "ge0": lambda x: f"(({x}) >= 0)", "le0": lambda x: f"(({x}) <= 0)",
        "limit": None, "pwl_derivative": None, "ddt": None, "vec": None, "var": None,
    },
    ("ngspice", "xyce"): {
        "log": "ln",
        "pwr": {True: "pwrs", False: lambda x, y: f"pow(abs({x}), {y})"},
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
# The power operator where its meaning differs, by context (True: behavioral): how the
# target writes ``base ^ exponent``. ngspice: |x|^y in parameters (xpressn.c, without a
# compatibility mode), x^y for an integer y in behavioral expressions (PTpower). WRspice:
# x^y in both (cmath1.cc v_power, inpfuncs.cc PTpower); SpiceSharp: |x|^y in both
# (RealBuilder.cs, NodeTypes.Pow), pow(x, y) is x^y (HelperFunctions.Pow).
POWER = {
    ("ngspice", "wrspice"): {False: lambda a, b: f"(abs({a})^({b}))"},
    ("ngspice", "spicesharp"): {True: lambda a, b: f"pow({a}, {b})"},
}

# Expression variables with another name: a string, a tuple for one that exists in
# behavioral expressions only, "" for none. Xyce: temp is the temperature in C, freq and
# hertz the AC frequency, pi; ngspice: temper, hertz (inpptree.c, behavioral only), no pi
# in numparam (xpressn.c).
VARIABLES = {
    ("xyce", "ngspice"): {"temp": "temper", "freq": ("hertz",), "hertz": ("hertz",),
                          "pi": "3.141592653589793", "vt": ""},
    # WRspice device expressions know time, freq and omega (inpptree.c specSigs); what
    # freq is outside an AC analysis is not stated.
    ("ngspice", "wrspice"): {"hertz": ""},
    # SpiceSharpParser: TEMP in C, TIME, FREQ (a constant 0 in parameters), PI, E
    # (SpiceEvaluationContext.cs).
    ("ngspice", "spicesharp"): {"temper": "temp", "hertz": ""},
}
# Signal accessors in expressions.
PROBES = {"v", "i", "vr", "vi", "vm", "vp", "vdb", "ir", "ii", "im", "ip", "idb"}

# Transient source functions. Xyce: getSourceFunctionID; ngspice: vsrc.c, isrc.c; WRspice:
# spSources.hlp, Tran Functions, with sin(a,b) a math function when commas separate the
# arguments, so the target writes them with blanks.
SOURCE_FUNCTIONS = {
    "xyce": {"pulse", "sin", "exp", "sffm", "pwl", "pat"},
    "ngspice": {"pulse", "sin", "sine", "exp", "sffm", "pwl", "am", "trnoise", "trrandom"},
    "wrspice": {"pulse", "sin", "exp", "sffm", "pwl"},
    # SpiceSharpParser: SpiceObjectMappings.cs waveforms, AM and SFFM in ngspice's argument
    # order (AMGenerator.cs, SFFMGenerator.cs).
    "spicesharp": {"pulse", "sin", "sine", "exp", "sffm", "pwl", "am"},
}
SOURCE_NAMES = {("ngspice", "xyce"): {"sine": "sin"}, ("ngspice", "wrspice"): {"sine": "sin"}}
BLANK_ARGUMENTS = {"wrspice"}
# Targets that read DC and AC followed by their values, not as assignments (Xyce;
# SpiceSharpParser, SourceGenerator.cs).
SOURCE_KEYWORDS = {"xyce", "spicesharp"}
# What a pulse with a zero rise or fall time rises in: Xyce zero (Reference Guide table
# 6-1), ngspice the time step (vsrcload.c), WRspice the time step (inptran.cc), SpiceSharp
# zero (Pulse.cs: a stated time is taken as stated).
PULSE_ZERO_EDGE = {"xyce": "zero", "ngspice": "the time step", "wrspice": "the time step",
                   "spicesharp": "zero"}
# Source functions whose arguments the target reads in part only: a test of the arguments
# inside the parentheses and the words after them. SpiceSharpParser: EXP takes exactly
# six (ExpGenerator.cs), PULSE seven, SIN six at most (PulseGenerator.cs, SineGenerator.cs),
# PWL no R or TD (PwlGenerator.cs reads them in the LTspice dialect only).
def _pwl_without_keys(args: list[str], after: list[str]) -> bool:
    keys = {after[k] for k in range(len(after) - 1) if after[k + 1] == "="}
    return "=" not in args and not keys & {"r", "td"}


SOURCE_ARGUMENTS = {"spicesharp": {
    "exp": lambda args, after: len(args) == 6,
    "pulse": lambda args, after: len(args) <= 7,
    "sin": lambda args, after: len(args) <= 6, "sine": lambda args, after: len(args) <= 6,
    "pwl": _pwl_without_keys,
}}

# B and E/G with an expression in the target: the keyword of an E/G expression and
# whether the expression is braced. Xyce: VALUE={expr} (Reference Guide, E and G);
# WRspice: ``function expr`` (spSources.hlp, Dependent Sources); its device expressions
# are parsed until they end (inpptree.cc getTree), bare. ngspice reads every form.
BEHAVIORAL = {"xyce": ("value", True), "wrspice": ("function", False),
              # SpiceSharpParser has no vol= or cur= (VoltageSourceGenerator.cs).
              "spicesharp": ("value", True)}
# Targets whose behavioral expressions have no ternary operator (WRspice: inpptree.cc
# bad_ops).
NO_TERNARY = {"wrspice"}

# Dot commands of the body with another name in the target, and the ones it has no
# equivalent for. NOT_BODY lines (analyses, outputs) are dropped, as in a deck.
DOTS = {
    ("xyce", "ngspice"): {".global_param": ".param", ".dcvolt": ".ic", ".incl": ".include"},
    # ngspice takes every command that starts with .param as .param (inpcom.c, ciprefix).
    ("ngspice", "xyce"): {".incl": ".include", ".params": ".param"},
    # WRspice: a function is a .param with arguments (spInput.hlp, .param Line).
    ("ngspice", "wrspice"): {".incl": ".include", ".params": ".param", ".func": ".param"},
    ("ngspice", "spicesharp"): {".incl": ".include", ".params": ".param"},
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
#   cshunt, rseries (elements added to every node or inductor). WRspice
#   (analysis/optsetp.cc): defad, defas, defl, defw; no scale, rshunt, cshunt, rseries.
OPTION_MAP = {
    ("xyce", "ngspice"): {"scale": "scale", "model_binning=false": None},
    ("ngspice", "xyce"): {"scale": "parser scale", "defad": None, "defas": None, "defl": None,
                          "defw": None, "rshunt": None, "cshunt": None, "rseries": None},
    ("ngspice", "wrspice"): {"scale": None, "defad": "defad", "defas": "defas", "defl": "defl",
                             "defw": "defw", "rshunt": None, "cshunt": None, "rseries": None},
    # SpiceSharpParser (OptionsControl.cs): none of them, another option is an error.
    ("ngspice", "spicesharp"): {k: None for k in ("scale", "defad", "defas", "defl", "defw",
                                                  "rshunt", "cshunt", "rseries")},
}
# Subcircuit parameters in WRspice take the value of the outermost scope that defines the
# name unless parhier is local (subexpand.cc); ngspice's take the innermost.
SCOPE_OPTION = {"wrspice": ".options parhier=local"}
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
    # WRspice keys (devlib IFkeys): a v i e f g h (sources), r c l k, s w, t o, u, d q j z
    # m, b (Josephson junction).
    ("ngspice", "wrspice"): {"a": "XSPICE code model", "n": "OSDI device",
                             "p": "coupled lines (P)", "y": "lossy line (Y)"},
    # SpiceSharpParser (SpiceObjectMappings.cs): R L C K B V H E I G F S W Q D M X J T.
    ("ngspice", "spicesharp"): {"a": "XSPICE code model", "n": "OSDI device",
                                "p": "coupled lines (P)", "y": "lossy line (Y)",
                                "u": "RC line (U)", "o": "lossy line (O)", "z": "MESFET (Z)"},
}

# Whether the target writes PARAMS: before the parameters of a .subckt or X line: Xyce
# (Reference Guide 2.1.37) does; ngspice reads it and parameters without it; WRspice
# (spInput.hlp, Subcircuits) knows no such keyword and would read it as a node.
PARAMS_KEYWORD = {"xyce": True, "wrspice": False}

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

    def render(self, target: str) -> str:
        """The statement as the target reads it: unchanged text where nothing differs."""
        if self.title:
            return self.raw
        if not self.tokens:
            return _comment_lines(self.raw, target)
        parts = [(_comments(t.ws, target), t.text) for t in self.tokens]
        if target == "xyce":                    # an indented line is a comment in Xyce
            parts[0] = ("", parts[0][1])
        tail = _comments(self.tail, target)
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


def comment_line(line: str, dialect: str) -> bool:
    """Whether a dialect reads a whole line as a comment: ``*`` or an inline mark first,
    and in Xyce a line that starts with a blank and does not continue a statement
    (Reference Guide 2.1.39.1, SpiceSeparatedFieldTool)."""
    s = line.lstrip(" \t")
    if not s.strip():
        return False
    if s[0] == "*" or _comment_at(s, 0, COMMENT[dialect]):
        return True
    return dialect == "xyce" and line[:1] == " " and s[0] != "+"


def _comments(ws: str, target: str) -> str:
    """The comments in the text between two tokens as the target reads them: an inline
    comment with a mark of the target, a comment line between continuation lines with ``*``."""
    lines = ws.split("\n")
    for k, line in enumerate(lines):
        s = line.lstrip(" \t")
        if k and s[:1] not in ("", "+"):
            lines[k] = _as_comment(line, target)
            continue
        m = re.search(r"\$|//|;", line)
        if m and line[m.start():m.end()] not in COMMENT[target]:
            lines[k] = line[:m.start()] + COMMENT_MARK[target] + line[m.end():]
    return "\n".join(lines)


def _as_comment(line: str, target: str) -> str:
    """A comment line as a comment line of the target, which does not execute it."""
    if not comment_line(line, target):
        line = "*" + line.lstrip(" \t")
    s = line.lstrip(" \t")
    if s.startswith(EXECUTED_COMMENTS.get(target, ())):
        line = "* " + s[1:]
    return line


def _comment_lines(text: str, target: str) -> str:
    """Comment and blank lines, each a comment line of the target as well."""
    return "".join(_as_comment(line, target) if line.strip() else line
                   for line in text.splitlines(keepends=True))


_CLOSING = {"{": "}", "(": ")"}


def _close(s: str, i: int) -> int:
    """The index after the brace or parenthesis that closes the one at ``i``."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == s[i]:
            depth += 1
        elif s[j] == _CLOSING[s[i]]:
            depth -= 1
            if depth == 0:
                return j + 1
    return len(s)


_BREAK = set(" \t\r\n(){},='\"")


def tokenize(raw: str, dialect: str) -> tuple[list[Token], str]:
    marks = COMMENT[dialect]
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
            end = raw.find("\n", i)
            end = n if end < 0 else end
            if toks and comment_line(raw[i:end], dialect):
                i = end
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
    dialect = FAMILY[dialect]
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
        elif not s.strip() or comment_line(line, dialect):
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
        first = next((l for l in st.raw.splitlines() if l.strip()), "")
        if first and not comment_line(first, dialect):
            st.tokens, st.tail = tokenize(st.raw, dialect)
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
    builtin: dict[str, str] = field(default_factory=dict)           # model -> device letter
    replace_ground: bool = False                # Xyce .preprocess replaceground true
    hspice_math: bool = False                   # Xyce .options parser hspice_ext with math


def route(source: str, target: str) -> list[tuple[str, str]]:
    """The pairs of rules that take a body from ``source`` to ``target``: one where the
    pair has rules, two through the hub otherwise, none within a family."""
    src, tgt = FAMILY.get(source), FAMILY.get(target)
    if src and src == tgt:
        return []
    if (src, tgt) in PAIRS:
        return [(src, tgt)]
    if (src, HUB) in PAIRS and (HUB, tgt) in PAIRS:
        return [(src, HUB), (HUB, tgt)]
    raise Untranslatable(f"no translation from {source} to {target}")


class Translator:
    def __init__(self, source: str, target: str):
        """``source`` and ``target``: a pair of PAIRS."""
        self.src, self.tgt = source, target
        self.pair = (self.src, self.tgt)
        self.ctx = Context()
        self.file = Path()                      # the file being translated
        self.modules: dict[str, str] = {}       # Verilog-A module -> version
        self.globals: set[str] = set()          # global nodes the target has to declare
        self.analyses: set[str] = set()         # the analyses the circuit runs
        self.depth = 0                          # subcircuit definitions around the statement
        self.in_deck = False                    # the file translated is the deck

    # ----------------------------------------------------------------- context

    def read_context(self, statements: list[Statement]) -> None:
        sub = None
        for st in statements:
            w = st.words()
            if not w:
                continue
            assigned = {w[i - 1] for i in range(2, len(w)) if w[i] == "="}
            if w[0] in (".param", ".params", ".global_param"):
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
                if w[2] in VA_BUILTIN.get(self.tgt, {}):
                    self.ctx.builtin[w[1]] = VA_BUILTIN[self.tgt][w[2]][0]
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

    def header(self) -> list[str]:
        """Lines the translated deck needs after its title: the global nodes it declares,
        the target's option for ngspice's scope of subcircuit parameters (SCOPE_OPTION)."""
        lines = [f".global {' '.join(sorted(self.globals))}"] if self.globals else []
        scoped = any(self.ctx.declared.values()) or any(self.ctx.inner.values()) or \
            any(self.ctx.passed.values())
        if scoped and self.tgt in SCOPE_OPTION:
            lines.append(SCOPE_OPTION[self.tgt])
        return lines

    # ------------------------------------------------------------- expressions

    def expression(self, text: str, behavioral: bool) -> str:
        """A whole expression in the target: its functions, and in a behavioral one of a
        target without the ternary operator (NO_TERNARY) every ``?:`` as a selection."""
        power = POWER.get(self.pair, {}).get(behavioral)
        if power and ("^" in text or "**" in text):
            text = _powers(text, power)             # before the functions, which may write ^
        new = self.expr(text, behavioral)
        if self.tgt in NO_TABS:
            new = new.replace("\t", " ")
        return _selects(new) if behavioral and self.tgt in NO_TERNARY else new

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
                if isinstance(rule, dict):
                    if rule[behavioral] is None and rule[not behavioral] is not None:
                        raise Untranslatable(f"expression function {low}() "
                                             f"{'in' if behavioral else 'outside'} a behavioral source")
                    rule = rule[behavioral]
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
            rule = VARIABLES.get(self.pair, {}).get(low) if low not in self.ctx.params else None
            if rule is None and self.src == "xyce" and low in ("time", "freq", "hertz") and \
                    not behavioral and low not in self.ctx.params:
                raise Untranslatable(f"{low} in a parameter expression (ngspice evaluates "
                                     f"those once)")
            if isinstance(rule, tuple):
                if not behavioral:
                    raise Untranslatable(f"expression variable {low} outside a behavioral source")
                out.append(rule[0])
            elif rule == "":
                raise Untranslatable(f"expression variable {low}")
            elif rule:
                out.append(rule)
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
        if self.tgt == "ngspice" and dev[:1] not in Ngspice.BRANCH:
            raise Untranslatable(f"current of a {dev[:1].upper()} device in an expression")
        return inner

    def hier(self, name: str) -> str:
        """A node inside a subcircuit in the target's form (HIER)."""
        (sep, down), (new_sep, new_down) = HIER[self.src], HIER[self.tgt]
        parts = name.split(sep)
        return new_sep.join(parts if down == new_down else reversed(parts))

    def node(self, name: str) -> str:
        """A node name in the target: the source's ground names become 0, a name that is
        ground only in the target gets a suffix."""
        low = name.lower()
        if low in self.ground(self.src):
            return "0"
        if low in self.ground(self.tgt):
            return name + "_"
        if name[:1] == "$" and self.tgt == "ngspice":
            # A Xyce node named $G... is global (Reference Guide 2.3.1); in ngspice a $
            # after a blank starts a comment, and .global makes a node global.
            if low[:2] != "$g":
                raise Untranslatable(f"node {name}: $ starts a comment in ngspice")
            self.globals.add(name[1:])
            return name[1:]
        return name

    def ground(self, dialect: str) -> tuple[str, ...]:
        """Ground names besides 0. Xyce's only under .preprocess replaceground."""
        return GROUND[dialect] if dialect != "xyce" or self.ctx.replace_ground else ()

    # -------------------------------------------------------------- statements

    def statements(self, statements: list[Statement], deck: bool) -> list[Statement]:
        out: list[Statement] = []
        end = None
        self.depth = 0
        self.in_deck = deck
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
            self.depth += head in (".subckt", ".macro")
            if head in (".ends", ".eom"):
                if not self.depth:              # Xyce passes over an .ends without .subckt
                    continue
                self.depth -= 1
            out += self.statement(st)
        return out

    def statement(self, st: Statement) -> list[Statement]:
        head = st.head
        if head[0] == ".":
            return self.dot(st)
        if not head[0].isalpha():
            raise Untranslatable(f"statement {st.tokens[0].text!r}")
        letter = head[0]
        if letter == "n" and self.src == "ngspice":         # OSDI instance of a built-in
            model = next((t for t in st.words()[1:] if t in self.ctx.builtin), None)
            if model:
                st.set(0, self.ctx.builtin[model] + st.tokens[0].text)
                letter = self.ctx.builtin[model]
        if letter in NO_ELEMENT[self.pair]:
            raise Untranslatable(NO_ELEMENT[self.pair][letter])
        self.braces(st)
        no = NO_INSTANCE_PARAMS.get(self.pair, {}).get(letter, {})
        bad = [x for i, x in enumerate(st.words()[:-1]) if x in no and st.words()[i + 1] == "="]
        if bad:
            raise Untranslatable(f"{letter.upper()} parameter {bad[0]}: {no[bad[0]]}")
        if letter == "k":
            return self.mutual(st)
        if letter in "rcl" and self.src == "xyce":
            self.passive(st)
            self.tc(st)
        if letter in "vi":
            self.source(st)
        elif letter == "b" or letter in "eg" and any(w in ("value", "vol", "cur") for w in st.words()):
            self.behavioral(st)
        if letter in NODES or letter == "x":
            self.nodes(st)
        if letter == "x":
            self.params_keyword(st)
            self.call_scope(st)
        if letter == "q" and self.tgt in EMITTER_SUBSTRATE:
            self.substrate(st)
        if letter == "c" and self.tgt in CAPACITOR_MODEL_GEOMETRY and \
                any(self.model(x) for x in st.words()[3:4]) and "l" not in st.words():
            raise Untranslatable(f"capacitor model without l ({self.tgt} computes it from the geometry)")
        self.multiplier(st)
        if letter in LETTERS.get(self.pair, {}):
            st.set(0, LETTERS[self.pair][letter] + st.tokens[0].text)
        return [st]

    def substrate(self, st: Statement) -> None:
        """A Q with three terminals: its substrate is ground in ngspice (bjt.c), stated."""
        w = st.words()
        at = next((i for i in range(4, len(w)) if self.model(w[i])), None)
        if at == 4:
            st.tokens.insert(4, Token(" ", "0"))
            st.edited = True

    def call_scope(self, st: Statement) -> None:
        """SpiceSharpParser evaluates an X line parameter in the subcircuit's scope, unless
        it is the name itself (EvaluationContext.cs, SubCircuitGenerator.cs); ngspice in
        the caller's. An expression that names a parameter of the subcircuit differs."""
        if self.tgt not in CALLEE_SCOPE:
            return
        w = st.words()
        sub, at = _subckt_of(w)
        inside = self.ctx.declared.get(sub, set()) | self.ctx.inner.get(sub, set())
        for i in range(at + 1, len(w) - 2):
            if w[i + 1] != "=" or w[i + 2].strip("{}'") == w[i]:
                continue
            names = {m.lower() for m in _IDENT.findall(w[i + 2])}
            if names & inside:
                raise Untranslatable(f"X line parameter {w[i]}={st.tokens[i + 2].text} names a "
                                     f"parameter of the subcircuit")

    def multiplier(self, st: Statement) -> None:
        """m on an element whose letter or model the target has no multiplier for."""
        w = st.words()
        if not any(w[i] == "m" and w[i + 1] == "=" for i in range(1, len(w) - 1)):
            return
        no = NO_MULTIPLIER.get(self.tgt, set())
        letter = w[0][0]
        model = next((self.model_name(x) for x in w[1:] if self.model(x)), None)
        if letter in no or model in no:
            raise Untranslatable(f"multiplier m on a {letter.upper()} device"
                                 f"{f' ({model})' if model else ''} in {self.tgt}")

    def model_name(self, name: str) -> str | None:
        """The model a card selects in the source: its family and level (LEVELS)."""
        n = name.lower()
        typ, level = self.ctx.models.get(n) or self.ctx.models[n.split(".")[0]]
        try:
            lvl = int(number(level)) if level else 1
        except Unsupported:
            return None
        return LEVELS[self.src].get((FAMILY_OF_TYPE.get(typ), lvl))

    def params_keyword(self, st: Statement) -> None:
        """PARAMS: on a .subckt or X line as the target writes it (PARAMS_KEYWORD)."""
        want = PARAMS_KEYWORD.get(self.tgt)
        if want:
            _params_keyword(st)
        elif want is False and any(t.text.lower() == "params:" for t in st.tokens):
            k = next(i for i, t in enumerate(st.tokens) if t.text.lower() == "params:")
            ws = st.tokens.pop(k).ws
            if k < len(st.tokens):
                st.tokens[k].ws = st.tokens[k].ws or ws
            st.edited = True

    # ------------------------------------------------------------- dot commands

    def dot(self, st: Statement) -> list[Statement]:
        w = st.words()
        head = w[0]
        if head in NO_DOT[self.src]:
            raise Untranslatable(NO_DOT[self.src][head])
        rename = DOTS[self.pair].get(head)
        if rename:
            st.set(0, rename)
        if (rename or head) in (".param", ".global_param", ".func"):
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
            if self.pair == ("ngspice", "wrspice"):
                self.inherit(st, w[1])
            self.params_keyword(st)
        elif head in (".ic", ".nodeset", ".dcvolt"):
            self.braces(st)
            if "(" not in w:                    # Xyce .DCVOLT form: node value pairs
                st.tokens[1:] = [Token(" ", f"v({self.hier(self.node(a.text))})={b.text}")
                                 for a, b in zip(st.tokens[1::2], st.tokens[2::2])]
                st.edited = True
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
        if self.tgt in CASE_SENSITIVE_NAMES:
            self.names_in_case(st)
        return [st]

    def names_in_case(self, st: Statement) -> None:
        """Dot commands, library sections in lower case, .ends without its name: compared
        case-sensitively by SpiceSharpParser (LibProcessor.cs, ParseTreeEvaluator.cs). A
        section in the deck itself it reads as a file to include."""
        w = st.words()
        if st.tokens[0].text != w[0]:
            st.set(0, w[0])
        if w[0] == ".ends" and len(w) > 1:
            del st.tokens[1:]
            st.edited = True
        elif w[0] in (".lib", ".endl") and len(w) > 1:
            if w[0] == ".lib" and len(w) == 2 and self.in_deck:
                raise Untranslatable(f"library section in the deck ({self.tgt} reads it as a file)")
            last = len(w) - 1
            if (w[0] == ".endl" or len(w) == 2 or last == 2) and st.tokens[last].text != w[last]:
                st.set(last, w[last])

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
        toks, tail = tokenize(line, self.tgt)
        return [Statement(line, toks, tail)]

    def declare(self, st: Statement, sub: str) -> None:
        """Xyce takes X line parameters a subcircuit does not declare (Reference Guide
        2.1.37), and they override a .param inside it; ngspice takes declared ones only.
        A parameter only passed is declared, with the global of its name as default."""
        extra = self.ctx.passed.get(sub, set()) - self.ctx.declared.get(sub, set())
        if extra & self.ctx.inner.get(sub, set()):
            raise Untranslatable("X line parameter overrides a .param inside the subcircuit")
        for name in sorted(extra):
            default = self.quoted(name) if name in self.ctx.globals else "0"
            st.tokens += [Token(" ", name), Token("", "="), Token("", default)]
            st.edited = True

    def inherit(self, st: Statement, sub: str) -> None:
        """WRspice takes X line parameters a subcircuit does not declare and sees the
        enclosing scope inside it (subexpand.cc): a default that is the parameter of the
        enclosing scope (the form declare() writes) goes, the name would refer to itself.
        An X line parameter that a .param inside sets is the X line's in WRspice
        (spInput.hlp, Subcircuit Parameters), the .param's in ngspice."""
        if self.ctx.passed.get(sub, set()) & self.ctx.inner.get(sub, set()):
            raise Untranslatable("X line parameter that a .param inside the subcircuit sets")
        w = st.words()
        for i in range(len(w) - 3, 1, -1):
            if w[i + 1] == "=" and w[i + 2].strip("{}'") == w[i]:
                ws = st.tokens[i].ws
                del st.tokens[i:i + 3]
                if i < len(st.tokens):
                    st.tokens[i].ws = st.tokens[i].ws or ws
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
            if start == close + 1 and st.head == ".param":     # a function as a .param
                st.tokens.insert(start, Token(" ", "="))
                st.edited = True
                start += 1
                w = st.words()
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
            new = self.expression(body, behavioral=False)
            quote = braced and text[0] not in READ_QUOTES[self.tgt] or \
                len(toks) > 1 and self.tgt in ONE_TOKEN_VALUES
            if new != body or quote:
                new = self.quoted(new) if braced or quote else new
                st.tokens[start:end] = [Token(toks[0].ws, new)]
                st.edited = True

    def quoted(self, text: str) -> str:
        """An expression delimited as the target evaluates it when reading (QUOTE)."""
        a, b = QUOTE[self.tgt]
        return a + text + b

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
                raise Untranslatable(f"{typ} model parameter {w[k]} (the value of an instance "
                                     f"in ngspice, not in {self.tgt})")
            if k is not None:                   # moved onto the instances, see passive()
                ws = st.tokens[k].ws
                del st.tokens[k:k + 3]
                if k < len(st.tokens):
                    st.tokens[k].ws = st.tokens[k].ws or ws
                st.edited = True
        new = TYPE_NAMES.get(self.pair, {}).get(typ)
        if new:
            st.set(2, new)
        if typ in FAMILY_OF_TYPE:
            self.level(st, FAMILY_OF_TYPE[typ])
            return
        if typ in VA_BUILTIN.get(self.tgt, {}):
            self.builtin(st, typ)
            return
        if typ in TYPES[self.tgt]:
            self.flags(st, typ)
            return
        if not new:
            raise Untranslatable(f"model type {typ}")

    def flags(self, st: Statement, typ: str) -> None:
        """Model flags written without a value (ngspice's LTRA): Xyce wants flag=1."""
        table = FLAGS.get(self.pair, {}).get(typ)
        if not table:
            return
        w = st.words()
        for i in range(len(w) - 1, 2, -1):
            bare = w[i] not in ("(", ")", "=") and w[i - 1] != "=" and \
                (i + 1 >= len(w) or w[i + 1] != "=")
            if not bare:
                continue
            if w[i] not in table:
                raise Untranslatable(f"{typ} model flag {w[i]}")
            if table[w[i]] is None:
                del st.tokens[i]
            else:
                st.set(i, f"{table[w[i]]}=1")
            st.edited = True

    def builtin(self, st: Statement, module: str) -> None:
        """A model of a Verilog-A module the target has built in, if the versions agree."""
        _, types, level, version = VA_BUILTIN[self.tgt][module]
        have = self.modules.get(module)
        if have is None or have.split(".")[:2] != version.split("."):
            raise Untranslatable(f"Verilog-A {module} {have or '(version unknown)'}: "
                                 f"{self.tgt} has {version}")
        w = st.words()
        k = next((i for i in range(3, len(w) - 2) if w[i] == "type" and w[i + 1] == "="), None)
        sign = number(w[k + 2]) if k is not None else 1
        if k is not None:
            del st.tokens[k:k + 3]
        st.set(2, types[0] if sign > 0 else types[1])
        _add_param(st, "level", str(level))

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
        by_version = LEVEL_OF_VERSION.get((self.tgt, model))
        if family in NO_LEVEL.get(self.tgt, ()):
            if k is not None:
                ws = st.tokens[k].ws
                del st.tokens[k:k + 3]
                if k < len(st.tokens):
                    st.tokens[k].ws = st.tokens[k].ws or ws
                st.edited = True
            return
        if by_version:
            computed = self.computed_version(st, model)
            near = [v for v in by_version if v[:2] == computed[:2]]
            if not near:
                raise Untranslatable(f"{model} {_dotted(computed)} of {self.src}: {self.tgt} has "
                                     f"{', '.join(_dotted(v) for v in by_version)}")
            new = by_version[min(near, key=lambda v: abs(v[2] - computed[2]))]
        else:
            new = lvl if lvl in target else target[0]
            self.version(st, model)
        if new != lvl:
            k = next((i for i in range(3, len(st.tokens) - 2) if st.tokens[i].text.lower() == "level"
                      and st.tokens[i + 1].text == "="), None)
            if k is None:
                _add_param(st, "level", str(new))
            else:
                st.set(k + 2, str(new))

    def computed_version(self, st: Statement, model: str) -> tuple[int, int, int] | None:
        """The version the source computes for a model card (VERSIONS), None where the
        source has one version only."""
        src = VERSIONS.get((self.src, model))
        if not src:
            return None
        w = st.words()
        k = next((i for i in range(3, len(w) - 2) if w[i] == "version" and w[i + 1] == "="), None)
        return src(_version(st.tokens[k + 2].text) if k is not None else None)

    def version(self, st: Statement, model: str) -> None:
        computed = self.computed_version(st, model)
        if computed is None:
            return
        text = _dotted(computed)
        tgt = VERSIONS[(self.tgt, model)](computed)
        if tgt[:2] != computed[:2]:
            raise Untranslatable(f"{model} {text} of {self.src}: {self.tgt} computes {_dotted(tgt)}")
        w = st.words()
        k = next((i for i in range(3, len(w) - 2) if w[i] == "version" and w[i + 1] == "="), None)
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
                new = self.expression(body, behavioral or bool(re.search(r"\b[vi]\s*\(", body, re.I)))
                if new != body or t.text[0] not in READ_QUOTES[self.tgt]:
                    st.set(i, self.quoted(new))
        if self.tgt != "ngspice":
            return
        positions = set(self.value_positions(st)) if st.head[0] != "." else set()
        for i, t in enumerate(st.tokens):
            if (i in positions or i > 1 and st.tokens[i - 1].text == "=") and \
                    t.text.lower() in self.ctx.params and not is_number(t.text):
                st.set(i, self.quoted(t.text))

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
        if self.depth and self.tgt in GLOBAL_COUPLING:
            raise Untranslatable(f"mutual inductor inside a subcircuit ({self.tgt} looks the "
                                 f"inductors up outside it)")
        w = st.words()
        names = [t.text for t in st.tokens[1:] if t.text.lower()[:1] == "l" and
                 not is_number(t.text) and t.text.lower() not in self.ctx.params]
        rest = st.tokens[1 + len(names):]
        if any(self.model(t.text) for t in rest):
            raise Untranslatable("nonlinear mutual inductor (core model)")
        if self.tgt == "ngspice" and len(rest) == 1 and rest[0].text.lower() in self.ctx.params:
            st.set(1 + len(names), self.quoted(rest[0].text))
        if len(names) <= 2 or self.tgt == "xyce":
            return [st]
        coupling = "".join(t.ws + t.text for t in rest).strip()
        name = st.tokens[0].text
        out = []
        for n, (a, b) in enumerate(combinations(names, 2)):
            raw = f"{name}{'' if n == 0 else f'_{n}'} {a} {b} {coupling}\n"
            toks, tail = tokenize(raw, self.tgt)
            out.append(Statement(raw, toks, tail))
        return out

    def source(self, st: Statement) -> None:
        w = st.words()
        if self.tgt in ONE_EXPRESSION and sum(x[:1] == "{" for x in w) > 1:
            raise Untranslatable(f"source with more than one expression ({self.tgt} takes one)")
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
            args, after = _function_args(w, i)
            edge = PULSE_ZERO_EDGE[self.src], PULSE_ZERO_EDGE[self.tgt]
            if new == "pulse" and edge[0] != edge[1] and \
                    any(is_number(a) and number(a) == 0 for a in args[3:5]):
                raise Untranslatable(f"pulse with zero rise or fall time ({edge[0]} in "
                                     f"{self.src}, {edge[1]} in {self.tgt})")
            check = SOURCE_ARGUMENTS.get(self.tgt, {}).get(new)
            if check and not check(args, after):
                raise Untranslatable(f"{new} source with arguments {self.tgt} does not read")
            if self.tgt in BLANK_ARGUMENTS:
                self.blank_arguments(st, i)
            self.dc_value(st, i)
            break
        w = st.words()
        if self.tgt in SOURCE_KEYWORDS:
            for i in range(len(w) - 1, 2, -1):
                if w[i] in ("dc", "ac") and i + 2 < len(w) and w[i + 1] == "=":
                    del st.tokens[i + 1]
                    st.tokens[i + 1].ws = st.tokens[i + 1].ws or " "
                    st.edited = True

    def blank_arguments(self, st: Statement, at: int) -> None:
        """The arguments of the source function at ``at`` separated by blanks, its R and
        TD inside the parentheses (WRspice, spSources.hlp: Tran Functions, Piece-Wise
        Linear); ngspice writes those after them."""
        if at + 1 >= len(st.tokens) or st.tokens[at + 1].text != "(":
            return
        depth, close = 0, None
        for k in range(at + 1, len(st.tokens)):
            depth += st.tokens[k].text == "("
            depth -= st.tokens[k].text == ")"
            if depth == 0:
                close = k
                break
        if close is None:
            return
        keys = []
        while close + 3 < len(st.tokens) and st.words()[close + 1] in ("r", "td") and \
                st.words()[close + 2] == "=":
            keys += st.tokens[close + 1:close + 4]
            del st.tokens[close + 1:close + 4]
        if keys:
            keys[0].ws = keys[0].ws or " "
            st.tokens[close:close] = keys
            st.edited = True
        for k in range(close - 1, at + 1, -1):
            if st.tokens[k].text == "," and _depth([t.text for t in st.tokens[at + 2:k]]) == 0:
                ws = st.tokens.pop(k).ws
                st.tokens[k].ws = st.tokens[k].ws or ws or " "
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

    def dc_value(self, st: Statement, at: int) -> None:
        """A source with a transient function and no DC value: in an OP or DC analysis
        Xyce takes 0 (Vsrc::loadDAEBVector), ngspice the function at t=0 (vsrcload.c);
        in a transient both start from the function. Exact where the circuit runs OP and
        DC only and the target is ngspice: DC 0 stated."""
        if not self.analyses & {"op", "dc"}:
            return
        before = st.words()[3:at]
        if "ac" in before:
            before = before[:before.index("ac")]
        if before:
            return                              # DC, or a value, is given
        if self.analyses - {"op", "dc"} or self.tgt != "ngspice":
            raise Untranslatable("source without a DC value in an OP or DC analysis (Xyce "
                                 "takes 0, ngspice the transient value at t=0)")
        st.tokens[at:at] = [Token(" ", "dc"), Token(" ", "0")]
        st.edited = True

    def tc(self, st: Statement) -> None:
        """Xyce takes TC=a,b for TC1=a TC2=b (Reference Guide, R and L parameters)."""
        w = st.words()
        k = next((i for i in range(3, len(w) - 1) if w[i] == "tc" and w[i + 1] == "="), None)
        if k is None:
            return
        values = [st.tokens[k + 2].text]
        if k + 4 < len(w) and w[k + 3] == ",":
            values.append(st.tokens[k + 4].text)
        new = [Token(st.tokens[k].ws, f"tc1={values[0]}")] + \
            [Token(" ", f"tc2={v}") for v in values[1:]]
        st.tokens[k:k + 2 * len(values) + 1] = new
        st.edited = True

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
        """B, and E/G with an expression, in the target's form (BEHAVIORAL); braces()
        has translated an expression in braces already."""
        form = BEHAVIORAL.get(self.tgt)
        if not form:
            return
        keyword, braced = form
        w = st.words()
        for i in range(len(w) - 2):
            if w[i] in ("v", "i", "value", "vol", "cur") and w[i + 1] == "=":
                if w[i] in ("value", "vol", "cur") and w[i] != keyword:
                    st.set(i, keyword)
                end = next((j for j in range(i + 3, len(w) - 1) if w[j + 1] == "=" and
                            _depth(w[i + 2:j]) == 0), len(w))
                first = st.tokens[i + 2].text
                if end == i + 3 and first[:1] in "{'" and len(first) > 1:
                    text = first[1:-1]              # translated by braces()
                else:
                    text = self.expression("".join(t.ws + t.text for t in st.tokens[i + 2:end])
                                           .strip(), behavioral=True)
                text = self.quoted(text) if braced else text
                if text != first or end > i + 3:
                    st.tokens[i + 2:end] = [Token(st.tokens[i + 2].ws, text)]
                    st.edited = True
                return


def _function_args(w: list[str], at: int) -> tuple[list[str], list[str]]:
    """The arguments of the source function at ``at``, inside its parentheses or up to the
    end, and the words after its parentheses."""
    if at + 1 < len(w) and w[at + 1] == "(":
        depth = 0
        for k in range(at + 1, len(w)):
            depth += w[k] == "("
            depth -= w[k] == ")"
            if depth == 0:
                return [x for x in w[at + 2:k] if x != ","], w[k + 1:]
    return [x for x in w[at + 1:] if x not in ("(", ")", ",")], []


def _subckt_of(w: list[str]) -> tuple[str, int]:
    """The subcircuit an X line instantiates and its index: the last name before the
    parameters."""
    k = next((i for i in range(1, len(w)) if w[i] in ("params:", "params") or
              i + 1 < len(w) and w[i + 1] == "="), len(w)) - 1
    return w[k], k


def _params_keyword(st: Statement) -> None:
    """PARAMS: before the first parameter of a .subckt or X line, the form the Xyce
    Reference Guide (2.1.37) gives; ngspice writes the parameters without it."""
    w = st.words()
    if "params:" in w:
        return
    k = next((i for i in range(2, len(w) - 1) if w[i + 1] == "="), None)
    if k is not None:
        st.tokens.insert(k, Token(st.tokens[k].ws, "params:"))
        st.tokens[k + 1].ws = st.tokens[k + 1].ws or " "
        st.edited = True


def _add_param(st: Statement, name: str, value: str) -> None:
    """``name=value`` at the end of a model card, inside its parentheses if it has them."""
    at = len(st.tokens) - 1 if st.tokens[-1].text == ")" else len(st.tokens)
    st.tokens[at:at] = [Token(" ", name), Token("", "="), Token("", value)]
    st.edited = True


def _depth(words: list[str]) -> int:
    return sum(w == "(" for w in words) - sum(w == ")" for w in words)


def _dotted(version: tuple[int, ...]) -> str:
    return ".".join(map(str, version))


def _version(text: str) -> tuple[int, int, int]:
    """'4.8.2', '4.82', '4.8', 4.8 -> (4, 8, 2), (4, 8, 2), (4, 8, 0), (4, 8, 0)."""
    t = text.strip("'\"{}")
    if "e" in t.lower() and is_number(t):     # 4.500000e+0
        t = f"{number(t):g}"
    parts = t.split(".")
    if len(parts) == 2 and len(parts[1]) == 2 and parts[1].isdigit():
        parts = [parts[0], parts[1][0], parts[1][1]]
    try:
        nums = [int(p) for p in parts[:3]]
    except ValueError:
        raise Untranslatable(f"model version {text}")
    return tuple(nums + [0] * (3 - len(nums)))


# ------------------------------------------------------------------------ files

def va_versions(files) -> dict[str, str]:
    """Verilog-A module -> the version its source states (``Version: 103.4.0``)."""
    out = {}
    for f in files:
        if f.suffix.lower() == ".va":
            m = re.search(r"Version:\s*(\d+(?:\.\d+)+)", f.read_text(encoding="latin-1"))
            for module in netlist.parse(f, "veriloga").modules:
                out[module] = m.group(1) if m else ""
    return out


def translate_text(texts: dict[Path, tuple[str, bool]], source: str, target: str,
                   modules: dict[str, str] | None = None, analyses: set[str] = frozenset()
                   ) -> dict[Path, str]:
    """Each file's text in the target dialect. ``texts``: path -> (text, is the deck);
    ``modules``: the Verilog-A modules the body loads, with their versions; ``analyses``:
    the types of the analyses the circuit runs. A file whose statements need no change
    keeps its text."""
    out = {p: t for p, (t, _) in texts.items()}
    for src, tgt in route(source, target):
        out = _translate_pair({p: (out[p], deck) for p, (_, deck) in texts.items()}, src, tgt,
                              modules, analyses)
    return out


def _translate_pair(texts: dict[Path, tuple[str, bool]], source: str, target: str,
                    modules: dict[str, str] | None, analyses: set[str]) -> dict[Path, str]:
    tr = Translator(source, target)
    tr.modules = modules or {}
    tr.analyses = set(analyses)
    parsed = {p: parse(t, source, deck) for p, (t, deck) in texts.items()}
    for sts in parsed.values():
        tr.read_context(sts)
    out = {}
    for p, sts in parsed.items():
        tr.file = p
        new = tr.statements(sts, texts[p][1])
        out[p] = "".join(st.render(tr.tgt) for st in new)
    head = tr.header()
    if head:
        deck = next(p for p, (_, d) in texts.items() if d)
        title, _, rest = out[deck].partition("\n")
        out[deck] = title + "\n" + "".join(f"{line}\n" for line in head) + rest
    return out


def translate(case: Case, nl: Netlist, dest: Path, target: str, analyses: set[str]
              ) -> list[Path]:
    """Rewrite the body of ``nl`` staged under ``dest`` in place into ``target``: the deck
    and every netlist it reaches; a library file only where it needs a change. The files
    changed."""
    g = case.graphs[nl.file]
    files = [staged(dest, f) for f in sorted(g.files) if f.suffix.lower() not in netlist.VA_SUFFIXES]
    if any(f.suffix.lower() == ".gz" for f in files):
        raise Untranslatable("compressed netlist file")
    deck = staged(dest, case.directory / nl.file)
    texts = {p: (p.read_bytes().decode("latin-1"), p == deck) for p in files}
    out = translate_text(texts, nl.dialect, target, va_versions(g.files), analyses)
    changed = []
    for p, text in out.items():
        if text != texts[p][0]:
            p.write_bytes(text.encode("latin-1"))
            changed.append(p)
    return changed
