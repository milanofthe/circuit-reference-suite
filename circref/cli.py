"""python -m circref {validate,build,check,list}

build  writes every generated file (case and library READMEs, the top README tables).
check  validates and rebuilds in memory; fails when a committed file is stale.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from . import report
from .entry import ROOT, iter_cases, iter_libraries, load_case, validate_schema
from .validate import check_case, check_library


def load_candidates() -> list[dict]:
    return yaml.safe_load((ROOT / "candidates.yaml").read_text(encoding="utf-8"))


def _generated() -> dict[Path, bytes]:
    cases, libs = iter_cases(), iter_libraries()
    files = {c.directory / "README.md": report.case_readme(c).encode() for c in cases}
    files |= {lib.directory / "README.md": report.library_readme(lib).encode() for lib in libs}
    files[ROOT / "README.md"] = report.top_readme(cases, libs, load_candidates()).encode()
    return files


def cmd_validate(args) -> int:
    failed = False
    for e in validate_schema(load_candidates(), "candidates"):
        print(f"candidates.yaml: {e}")
        failed = True
    for lib in iter_libraries():
        for e in check_library(lib):
            print(f"libraries/{lib.id}: {e}")
            failed = True
    for c in [load_case(i) for i in args.ids] if args.ids else iter_cases():
        errors = check_case(c)
        for e in errors:
            print(f"{c.id}: error: {e}")
        failed |= bool(errors)
        if not errors:
            print(f"{c.id}: ok, {report.status_text(c)}")
    return int(failed)


def cmd_build(args) -> int:
    for path, data in _generated().items():
        if not path.exists() or path.read_bytes() != data:
            path.write_bytes(data)
            print(f"wrote {path.relative_to(ROOT).as_posix()}")
    return 0


def cmd_check(args) -> int:
    rc = cmd_validate(args)
    if rc:
        return rc
    stale = [p for p, data in _generated().items() if not p.exists() or p.read_bytes() != data]
    for p in stale:
        print(f"stale: {p.relative_to(ROOT).as_posix()} (run python -m circref build)")
    return int(bool(stale))


def cmd_list(args) -> int:
    for c in iter_cases():
        print(f"{c.id:44s} {c.family:16s} {report.status_text(c)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="circref")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("validate", cmd_validate), ("check", cmd_check)):
        sp = sub.add_parser(name)
        sp.add_argument("ids", nargs="*")
        sp.set_defaults(fn=fn)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
