"""Everything CI checks before a case or library is accepted."""
from __future__ import annotations

from .entry import (GENERATED, ROOT, Case, Entry, Library, load_library, sha256,
                    validate_schema)


def check_files(entry: Entry, descriptor: str) -> list[str]:
    """Every committed file is listed, every listed file is committed, and the
    upstream originals still hash to what upstream hashed to."""
    out = []
    listed = {f["path"]: f for f in entry.files()}
    on_disk = {p.relative_to(entry.directory).as_posix()
               for p in entry.directory.rglob("*") if p.is_file()}
    on_disk -= {descriptor, *GENERATED}
    for path in sorted(on_disk - listed.keys()):
        out.append(f"{path}: committed but not listed under files")
    for path, f in listed.items():
        if path not in on_disk:
            out.append(f"{path}: listed but not committed")
        elif "sha256" in f and sha256(entry.directory / path) != f["sha256"]:
            out.append(f"{path}: differs from upstream {entry.upstream(f)}")
    return out


def check_library(lib: Library) -> list[str]:
    errors = validate_schema(lib.raw, "library")
    if errors:
        return errors
    if lib.id != lib.directory.name:
        errors.append(f"id {lib.id!r} differs from directory name")
    for target in (t for t in lib.resolve_table().values() if t is not None):
        if not (ROOT / target).is_file():
            errors.append(f"resolve: {target} does not exist")
    return errors + check_files(lib, "library.yaml")


def check_case(case: Case) -> list[str]:
    errors = validate_schema(case.raw, "case")
    if errors:
        return errors
    if case.id != case.directory.name:
        errors.append(f"id {case.id!r} differs from directory name")
    errors += check_files(case, "case.yaml")
    listed = {f["path"] for f in case.files()}
    for n in case.netlists():
        if n.file not in listed:
            errors.append(f"netlist {n.file} is not listed under files")
    if errors:
        return errors
    for name, g in case.graphs.items():
        errors += g.errors()
        if not g.analyses:
            errors.append(f"{name}: runs no analysis")
    for lib in case.libraries():
        errors += [f"library {lib}: {e}" for e in check_library(load_library(lib))]
    return sorted(set(errors), key=errors.index)
