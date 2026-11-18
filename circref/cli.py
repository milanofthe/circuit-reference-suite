"""python -m circref {validate,build,check,list,run,summary}

build  writes every generated file (case and library READMEs, the top README tables).
check  validates and rebuilds in memory; fails when a committed file is stale.
run    runs every netlist on its simulator (circref/run.py), results into --out.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import tomllib

from . import report
from .entry import ROOT, iter_cases, iter_libraries, load_case, validate_schema
from .validate import check_case, check_library


def load_candidates() -> list[dict]:
    return tomllib.loads((ROOT / "candidates.toml").read_text(encoding="utf-8"))["candidate"]


def _generated() -> dict[Path, bytes]:
    cases, libs = iter_cases(), iter_libraries()
    files = {c.directory / "README.md": report.case_readme(c).encode() for c in cases}
    files |= {lib.directory / "README.md": report.library_readme(lib).encode() for lib in libs}
    files[ROOT / "README.md"] = report.top_readme(cases, libs, load_candidates()).encode()
    return files


def cmd_validate(args) -> int:
    failed = False
    for e in validate_schema(load_candidates(), "candidates"):
        print(f"candidates.toml: {e}")
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


def cmd_run(args) -> int:
    from . import run
    jobs = run.select(args.case, args.sim)
    shard = (int(os.environ.get("FALLLOW_SHARD_INDEX", 0)), int(os.environ.get("FALLLOW_SHARD_COUNT", 1)))
    return run.run(jobs, Path(args.out), args.jobs, args.timeout, args.memory, shard)


def cmd_summary(args) -> int:
    from . import run
    print(run.summary(Path(args.results)))
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
    sp = sub.add_parser("run")
    sp.add_argument("--case", action="append", default=[], help="case id or glob, repeatable")
    sp.add_argument("--sim", action="append", default=[], help="simulator name, repeatable")
    sp.add_argument("--jobs", type=int, default=int(os.environ.get("FALLLOW_CORES", os.cpu_count())))
    sp.add_argument("--timeout", type=float, default=600, help="seconds per netlist")
    sp.add_argument("--memory", type=float, default=4, help="GB address space per netlist")
    sp.add_argument("--out", default="/artifacts/run")
    sp.set_defaults(fn=cmd_run)
    sp = sub.add_parser("summary")
    sp.add_argument("results")
    sp.set_defaults(fn=cmd_summary)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
