"""Cases and model libraries, and the include graph that ties them together.

Both are a directory with a TOML descriptor and the upstream files, committed byte
for byte below ``source.root`` so relative includes between them still resolve.
Every other file is listed with a provenance that says how it was made. A reference
that leaves the directory (a PDK path, an OSDI binary) is mapped by the descriptor's
``resolve`` table onto a file in this repository, or onto ``null`` when nobody may
redistribute it (``false``), which makes the case incomplete.
"""
from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import tomllib
from collections import Counter
from dataclasses import dataclass, field
from functools import cached_property, lru_cache
from pathlib import Path


from . import netlist

ROOT = Path(__file__).resolve().parent.parent
CASE_DIR = ROOT / "cases"
LIB_DIR = ROOT / "libraries"
SCHEMA_DIR = ROOT / "schema"
GENERATED = ("README.md",)


@dataclass(frozen=True)
class Entry:
    directory: Path
    raw: dict

    @property
    def id(self) -> str:
        return self.raw["id"]

    @property
    def title(self) -> str:
        return self.raw["title"]

    @property
    def source(self) -> dict:
        return self.raw["source"]

    @property
    def rel(self) -> str:
        return self.directory.relative_to(ROOT).as_posix()

    def files(self) -> list[dict]:
        return self.raw["files"]

    def adapted(self) -> list[dict]:
        return [f for f in self.files() if "sha256" not in f]

    def upstream(self, f: dict) -> str:
        return f.get("upstream") or posixpath.join(self.source.get("root", ""), f["path"])

    def resolve_table(self) -> dict[str, str | bool]:
        return self.raw.get("resolve", {})


@dataclass(frozen=True)
class Library(Entry):
    pass


@dataclass(frozen=True)
class Netlist:
    file: str
    dialect: str
    note: str | None
    resolve: dict                   # takes precedence over the case's table in this run


@dataclass(frozen=True)
class Case(Entry):

    @property
    def family(self) -> str:
        return self.raw["family"]

    @property
    def cost(self) -> str | None:
        """The term of the run time the case weights (schema/case.schema.json)."""
        return self.raw.get("cost")

    @property
    def open_questions(self) -> list[str]:
        return self.raw.get("open_questions", [])

    def netlists(self) -> list[Netlist]:
        return [Netlist(n["file"], n["dialect"], n.get("note"), n.get("resolve", {}))
                for n in self.raw["netlists"]]

    @cached_property
    def graphs(self) -> dict[str, "Graph"]:
        return {n.file: walk(self, n) for n in self.netlists()}

    def libraries(self) -> list[str]:
        return sorted({lib for g in self.graphs.values() for lib in g.libraries})

    def status(self) -> tuple[str, list[str]]:
        """complete | adapted | incomplete, with the reasons. Derived from the data,
        never stated, so the label cannot drift from the content."""
        missing = sorted({e.ref.target for g in self.graphs.values() for e in g.edges
                          if e.missing})
        if self.open_questions or missing:
            return "incomplete", list(self.open_questions) + [
                f"not redistributable here: {m}" for m in missing]
        reasons = [f"{self.rel}/{f['path']}: {f['provenance']}" for f in self.adapted()]
        for lib in self.libraries():
            reasons += [f"library {lib}: {f['path']}: {f['provenance']}"
                        for f in load_library(lib).adapted()]
        return ("adapted" if reasons else "complete"), reasons


# --------------------------------------------------------------------- graph

@dataclass(frozen=True)
class Edge:
    origin: Path                # the file that holds the reference
    ref: netlist.Ref
    target: Path | None         # None: declared missing, or unresolvable
    missing: bool               # declared missing in a resolve table
    error: str | None = None


@dataclass
class Graph:
    """Everything one netlist pulls in."""
    edges: list[Edge] = field(default_factory=list)
    analyses: list[str] = field(default_factory=list)
    subckts: dict[str, Counter] = field(default_factory=lambda: {"": Counter()})
    libraries: set[str] = field(default_factory=set)
    files: set[Path] = field(default_factory=set)
    dialect: str = ""
    models: dict[str, str] = field(default_factory=dict)        # every file, libraries too
    # device type ("cap/2": model type and level) -> device module of a simulator install
    # ("wrspice:adms/cap"), for types that simulator builds only as a loadable module
    modules: dict[str, str] = field(default_factory=dict)
    control: bool = False
    veriloga: bool = False

    @property
    def kinds(self) -> Counter:
        return netlist.flat_kinds(self.subckts)

    @property
    def devices(self) -> int:
        return sum(self.kinds.values())

    def errors(self) -> list[str]:
        return [e.error for e in self.edges if e.error]


def owner(path: Path) -> Entry | None:
    try:
        kind, name = path.relative_to(ROOT).parts[:2]
    except ValueError:
        return None
    if kind == "cases":
        return load_case(name)
    if kind == "libraries":
        return load_library(name)
    return None


@lru_cache(maxsize=None)
def _listdir(directory: Path) -> frozenset[str]:
    return frozenset(os.listdir(directory))


@lru_cache(maxsize=None)
def is_file(path: Path) -> bool:
    """Like Path.is_file, but case-sensitive on every platform, as on the CI runner."""
    if not path.is_file():
        return False
    part = path
    while part != ROOT and part.is_relative_to(ROOT):
        if part.name not in _listdir(part.parent):
            return False
        part = part.parent
    return True


def _resolve(origin: Path, ref: netlist.Ref, local: dict) -> tuple[Path | None, bool, str | None]:
    return _resolve_cached(origin, ref, tuple(sorted(local.items())))


@lru_cache(maxsize=None)
def _resolve_cached(origin: Path, ref: netlist.Ref, local_items: tuple) -> tuple[Path | None, bool, str | None]:
    local = dict(local_items)
    entry = owner(origin)
    table = entry.resolve_table() if entry else {}
    if isinstance(entry, Case):
        table = {**table, **local}
    where = f"{origin.relative_to(ROOT).as_posix()}:{ref.line}"
    if ref.target in table:
        mapped = table[ref.target]
        if mapped is False:
            return None, True, None
        path = ROOT / mapped
        if not is_file(path):
            return None, False, f"{where}: {ref.target!r} maps to missing {mapped}"
    else:
        if Path(ref.target).is_absolute() or ref.target.startswith(("~", "$")):
            return None, False, f"{where}: absolute path {ref.target!r} needs a resolve entry"
        path = Path(os.path.normpath(origin.parent / ref.target))
        if not is_file(path):
            return None, False, f"{where}: cannot resolve {ref.target!r}"
    if ref.kind == "osdi" and path.suffix.lower() not in netlist.VA_SUFFIXES:
        return None, False, f"{where}: {ref.target!r} must map to its Verilog-A source"
    if ROOT not in path.parents:
        return None, False, f"{where}: {ref.target!r} leaves the repository"
    return path, False, None


def _modules(case: Case, nl: Netlist, models: dict[str, str], levels: dict[str, str]) -> dict[str, str]:
    """The device modules of a simulator install the deck's models need: a model type,
    or type and level (``cap/2``), that the resolve table maps onto ``<simulator>:<module>``,
    as WRspice builds Verilog-A and retired devices only as modules it loads."""
    table = {**case.resolve_table(), **nl.resolve}
    out = {}
    for name, kind in models.items():
        for key in (f"{kind}/{levels[name]}" if name in levels else None, kind):
            mapped = table.get(key)
            if isinstance(mapped, str) and re.fullmatch(r"[a-z]+:[\w.+-]+(/[\w.+-]+)*", mapped):
                out[key] = mapped
                break
    return out


def walk(case: Case, nl: Netlist) -> Graph:
    g = Graph(dialect=nl.dialect)
    start = case.directory / nl.file
    queue = [(start, nl.dialect, None, True)]
    seen: set = set()
    models: dict[str, str] = {}
    levels: dict[str, str] = {}
    osdi_devices: set[str] = set()
    va_types: set[str] = set()
    modules: set[str] = set()
    defined: set[str] = set()
    used: set[str] = set()
    asked: set[str] = set()
    while True:
        while queue:
            path, dialect, section, deck = queue.pop(0)
            if (path, section) in seen:
                continue
            seen.add((path, section))
            g.files.add(path)
            entry = owner(path)
            if isinstance(entry, Library):
                g.libraries.add(entry.id)
            parsed = netlist.parse(path, dialect, deck)
            models |= parsed.models
            levels |= parsed.levels
            g.veriloga |= dialect == "veriloga"
            osdi_devices |= parsed.osdi_devices
            va_types |= parsed.va_types
            defined |= set(parsed.instances) - {""}
            used |= {k[2:] for c in parsed.instances.values() for k in c if k.startswith("x:")}
            modules |= parsed.modules
            if section is None:
                refs = parsed.refs
            elif section in parsed.sections:
                refs = parsed.sections[section]
                if nl.dialect in netlist.NGSPICE_LIB:      # ngspice opens the includes of
                    refs = refs + [r for s, rs in parsed.sections.items()   # every section
                                   if s != section for r in rs if r.kind == "include"]
            else:
                g.edges.append(Edge(path, netlist.Ref("lib", path.name, section, 0), None, False,
                                    f"{path.relative_to(ROOT).as_posix()}: no section {section!r}"))
                continue
            if entry is case:
                g.control |= parsed.control
                g.analyses += [a for a in parsed.analyses if a not in g.analyses]
                for name, counts in parsed.instances.items():
                    g.subckts.setdefault(name, Counter()).update(counts)
            for ref in refs:
                target, missing, error = _resolve(path, ref, nl.resolve)
                g.edges.append(Edge(path, ref, target, missing, error))
                if target is not None and ref.kind != "data":
                    kind = "veriloga" if ref.kind in ("osdi", "va") else dialect
                    queue.append((target, netlist.dialect_of(target, kind),
                                  ref.section if ref.kind == "lib" else None, False))
        # A Verilog-A device (ngspice N instance, Xyce Y plugin) needs a module of its type.
        # Simulators often load those from an init file the deck never names, so the
        # resolve table maps the type itself onto the source.
        needed = ({models[m] for m in osdi_devices if m in models} | va_types) - modules - asked
        needed -= netlist.NGSPICE_N_BUILTIN
        g.models = models
        g.modules = _modules(case, nl, models, levels)
        if not needed:
            undefined = sorted(used - defined) if nl.dialect in netlist.SPICE else []
            if undefined:
                g.edges.append(Edge(start, netlist.Ref("subckt", undefined[0], None, 0), None,
                                    False, f"{nl.file}: subcircuit {', '.join(undefined[:5])} "
                                    f"used but defined nowhere it includes"))
            return g
        for t in sorted(needed):
            asked.add(t)
            ref = netlist.Ref("osdi", t, None, 0)
            table = {**case.resolve_table(), **nl.resolve}
            if t not in table:
                g.edges.append(Edge(start, ref, None, False,
                                    f"{nl.file}: device type {t!r} has no Verilog-A module; "
                                    f"map {t!r} in resolve"))
                continue
            target, missing, error = _resolve(start, ref, nl.resolve)
            g.edges.append(Edge(start, ref, target, missing, error))
            if target is not None:
                queue.append((target, "veriloga", None, False))


# --------------------------------------------------------------------- loading

_CACHE: dict[Path, Entry] = {}


def _load(cls, directory: Path, name: str) -> Entry:
    directory = directory.resolve()
    if directory not in _CACHE:
        raw = tomllib.loads((directory / name).read_text(encoding="utf-8"))
        _CACHE[directory] = cls(directory, raw)
    return _CACHE[directory]


def load_case(ref: str | Path) -> Case:
    d = Path(ref) if (Path(ref) / "case.toml").exists() else CASE_DIR / str(ref)
    return _load(Case, d, "case.toml")


def load_library(ref: str | Path) -> Library:
    d = Path(ref) if (Path(ref) / "library.toml").exists() else LIB_DIR / str(ref)
    return _load(Library, d, "library.toml")


def iter_cases() -> list[Case]:
    return [load_case(d) for d in sorted(CASE_DIR.iterdir()) if (d / "case.toml").exists()]


def iter_libraries() -> list[Library]:
    return [load_library(d) for d in sorted(LIB_DIR.iterdir()) if (d / "library.toml").exists()]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def _validator(name: str):
    import jsonschema
    from referencing import Registry, Resource
    schemas = {p.name: json.loads(p.read_text(encoding="utf-8"))
               for p in SCHEMA_DIR.glob("*.schema.json")}
    registry = Registry().with_resources(
        (k, Resource.from_contents(v)) for k, v in schemas.items())
    return jsonschema.Draft202012Validator(schemas[f"{name}.schema.json"], registry=registry)


def validate_schema(instance, name: str) -> list[str]:
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
            for e in _validator(name).iter_errors(instance)]
