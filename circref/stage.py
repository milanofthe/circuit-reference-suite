"""A netlist made runnable: copied with what its include graph reaches into a directory
that mirrors the repository, every reference the resolve table maps elsewhere rewritten
onto the copy, every OSDI load onto the Verilog-A source compiled for it."""
from __future__ import annotations

import hashlib
import os
import posixpath
import shutil
import subprocess
import threading
from pathlib import Path

from . import netlist
from .entry import ROOT, Case, Library, Netlist, owner


class StageError(Exception):
    pass


def staged(dest: Path, path: Path) -> Path:
    return dest / path.relative_to(ROOT)


def tail(text: str, n: int = 400) -> str:
    text = text.strip()
    return text if len(text) <= n else "..." + text[-n:]


def _rewrite(file: Path, line: int, old: str, new: str) -> bool:
    """Replace the reference written on ``line`` or the continuation lines after it."""
    lines = file.read_bytes().decode("latin-1").split("\n")
    for i in range(max(line - 1, 0), min(line + 50, len(lines))):
        if old in lines[i]:
            lines[i] = lines[i].replace(old, new, 1)
            file.write_bytes("\n".join(lines).encode("latin-1"))
            return True
    return False


class Compiler:
    """Verilog-A compiled to OSDI once per source, shared by every run that loads it."""

    def __init__(self, cache: Path):
        self.cache = cache
        self.locks: dict[str, threading.Lock] = {}
        self.guard = threading.Lock()

    def osdi(self, va: Path, sources: list[Path]) -> Path:
        h = hashlib.sha256()
        for p in [va, *sorted(set(sources) - {va})]:
            h.update(p.read_bytes())
        key = h.hexdigest()[:16]
        out = self.cache / f"{va.stem}-{key}.osdi"
        with self.guard:
            lock = self.locks.setdefault(key, threading.Lock())
        with lock:
            if not out.exists():
                out.parent.mkdir(parents=True, exist_ok=True)
                tmp = out.with_suffix(".tmp")
                r = subprocess.run(["openvaf", str(va), "-o", str(tmp)], capture_output=True,
                                   text=True, cwd=va.parent)
                if r.returncode or not tmp.exists():
                    raise StageError(f"openvaf {va.relative_to(ROOT)}: {tail(r.stdout + r.stderr)}")
                tmp.rename(out)
        return out


def stage(case: Case, nl: Netlist, dest: Path, osdi: bool, compiler: Compiler) -> tuple[Path, list[Path]]:
    """The staged netlist, and the OSDI files to load before it (device types the deck
    uses without loading them). ``osdi``: the simulator loads compiled Verilog-A."""
    g = case.graphs[nl.file]
    if g.errors() or any(e.missing for e in g.edges):
        raise StageError("references not available in this repository")
    shutil.copytree(case.directory, staged(dest, case.directory), symlinks=True)
    for f in g.files:
        if isinstance(owner(f), Library):
            target = staged(dest, f)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
    va = [f for f in g.files if f.suffix.lower() in netlist.VA_SUFFIXES]
    preload: list[Path] = []
    done = set()
    for e in g.edges:
        if e.target is None or (e.origin, e.ref) in done:
            continue
        done.add((e.origin, e.ref))
        if e.ref.kind == "osdi":
            if not osdi:
                raise StageError("Verilog-A model; this simulator does not load OSDI")
            new = compiler.osdi(e.target, va)
        else:
            new = staged(dest, e.target)
            if Path(os.path.normpath(e.origin.parent / e.ref.target)) == e.target:
                continue                                    # resolves as written
        if e.ref.line == 0:                                 # loaded by the simulator's init
            preload.append(new)
            continue
        origin = staged(dest, e.origin)
        rel = new.as_posix() if not new.is_relative_to(dest) else \
            posixpath.relpath(new.as_posix(), origin.parent.as_posix())
        if not _rewrite(origin, e.ref.line, e.ref.target, rel):
            raise StageError(f"{e.origin.relative_to(ROOT)}:{e.ref.line}: {e.ref.target!r} not found")
    return staged(dest, case.directory / nl.file), preload
