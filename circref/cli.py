"""python -m circref {validate,build,check,list,circuits,select,run,compare}

build  writes every generated file (case and library READMEs, index.csv, the netlists of
       generated cases, circref/generate.py).
check  validates and rebuilds in memory; fails when a committed file is stale. validate
       and check write the netlists of generated cases that are missing first.
select    prints the circuits a filter matches (circref/query.py).
run       runs the circuits a filter or a study (--study) selects on simulators
          (circref/bench.py), results into --out with the selection in selection.json.
compare   each run against the reference of its analysis, into OUT/compare.json, and
          the plots of OUT/plots (circref/plot.py).
circuits  writes a circuits/<name>.toml for every eligible netlist that has none yet.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import tomllib

from . import generate, query, report
from .circuit import iter_circuits
from .entry import ROOT, iter_cases, iter_libraries, load_case, validate_schema
from .validate import check_case, check_library


def load_candidates() -> list[dict]:
    return tomllib.loads((ROOT / "candidates.toml").read_text(encoding="utf-8"))["candidate"]


def _generated() -> dict[Path, bytes]:
    cases, libs = iter_cases(), iter_libraries()
    files = {c.directory / "README.md": report.case_readme(c).encode() for c in cases}
    files |= {lib.directory / "README.md": report.library_readme(lib).encode() for lib in libs}
    files[ROOT / "index.csv"] = report.index_csv(iter_circuits()).encode()
    return files


def cmd_validate(args) -> int:
    failed = False
    for e in validate_schema(load_candidates(), "candidates"):
        print(f"candidates.toml: {e}")
        failed = True
    for path in sorted((ROOT / "studies").glob("*.toml")):
        try:
            load_study(path)
        except query.FilterError as e:
            print(e)
            failed = True
    for lib in iter_libraries():
        for e in check_library(lib):
            print(f"libraries/{lib.id}: {e}")
            failed = True
    cases = [load_case(i) for i in args.ids] if args.ids else iter_cases()
    generate.write(cases)
    for c in cases:
        errors = check_case(c)
        for e in errors:
            print(f"{c.id}: error: {e}")
        failed |= bool(errors)
        if not errors:
            print(f"{c.id}: ok, {report.status_text(c)}")
    if not args.ids:
        for circ in iter_circuits():
            for e in circ.errors():
                print(f"circuits/{circ.name}.toml: error: {e}")
                failed = True
    return int(failed)


def cmd_build(args) -> int:
    for path in generate.write():
        print(f"wrote {path.relative_to(ROOT).as_posix()}")
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
        print(f"{c.id:44s} {c.family:16s} {c.cost or '-':18s} {report.status_text(c)}")
    return 0


def cmd_circuits(args) -> int:
    from . import circuit
    proposed, skipped = circuit.proposals()
    for name, c in proposed.items():
        print(f"wrote {circuit.write(name, c).relative_to(ROOT).as_posix()}")
    reasons: dict[str, int] = {}
    for _, why in skipped:
        key = why.split(":")[0] if ":" in why else why.split()[0]
        reasons[key] = reasons.get(key, 0) + 1
    for why, n in sorted(reasons.items(), key=lambda kv: -kv[1]):
        print(f"skipped {n:5d}  {why}")
    return 0


def load_study(path: str | Path) -> dict:
    """A study (schema/study.schema.json): a filter, and the parameters of its run."""
    study = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_schema(study, "study")
    if errors:
        raise query.FilterError(f"{path}: " + "; ".join(errors))
    query.compile_filter(study["select"])
    return study


def cmd_run(args) -> int:
    from . import bench
    from .adapters import ADAPTERS
    if args.study and args.filter:
        raise query.FilterError("a study brings its own filter; give one or the other")
    study = load_study(args.study) if args.study else {}
    plan = study.get("run", {})

    def given(flag, key, default):          # the command line, the study, the default
        return flag if flag not in (None, []) else plan.get(key, default)

    expr = args.filter or study.get("select")
    circuits = bench.select(expr)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True)
    (out / "selection.json").write_text(json.dumps(
        {"study": study or None, "filter": expr, "commit": head.stdout.strip() or None,
         "circuits": [c.name for c in circuits]}, indent=1) + "\n", encoding="utf-8")
    adapters = [ADAPTERS[n] for n in given(args.sim, "simulators", list(ADAPTERS))]
    shard = (int(os.environ.get("FALLLOW_SHARD_INDEX", 0)), int(os.environ.get("FALLLOW_SHARD_COUNT", 1)))
    return bench.run(circuits, adapters, given(args.level, "levels", list(bench.LEVELS)), out,
                     args.jobs, given(args.timeout, "timeout", 600), given(args.memory, "memory", 4),
                     given(args.threads, "threads", 1), shard, tuple(args.redo),
                     given(args.repeats, "repeats", 1), tuple(given(args.type, "types", [])))


def cmd_select(args) -> int:
    names = query.select(args.filter)
    print("\n".join(names))
    print(f"{len(names)} circuits", file=sys.stderr)
    return 0


def cmd_compare(args) -> int:
    from . import compare, plot
    out = Path(args.out)
    compare.write(out)
    for p in plot.plot(out):
        print(p)
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
    sub.add_parser("circuits").set_defaults(fn=cmd_circuits)
    sp = sub.add_parser("select")
    sp.add_argument("filter", nargs="?", help="expression over the columns of index.csv; all when none")
    sp.set_defaults(fn=cmd_select)
    sp = sub.add_parser("run")
    sp.add_argument("filter", nargs="?", help="expression over the columns of index.csv; all when none")
    sp.add_argument("--sim", action="append", default=[], help="simulator, repeatable; all when none")
    sp.add_argument("--jobs", type=int, default=int(os.environ.get("FALLLOW_CORES", os.cpu_count())))
    sp.add_argument("--study", help="a study file (schema/study.schema.json) in place of a filter")
    sp.add_argument("--timeout", type=float, help="seconds per analysis (600)")
    sp.add_argument("--memory", type=float, help="GB address space per run (4)")
    sp.add_argument("--redo", action="append", default=[],
                    help="status whose jobs in OUT run again, repeatable (errors always do)")
    sp.add_argument("--level", action="append", default=[],
                    help="precision level of bench.toml, repeatable; all when none")
    sp.add_argument("--threads", type=int, help="threads per simulator run, the same for all (1)")
    sp.add_argument("--repeats", type=int, help="runs per analysis shorter than run.repeat_below of bench.toml, timed by the minimum (1)")
    sp.add_argument("--type", action="append", default=[],
                    help="analysis type to run (op, dc, ac, tran), repeatable; all when none. Into an OUT of its own")
    sp.add_argument("--out", default="out")
    sp.set_defaults(fn=cmd_run)
    sp = sub.add_parser("compare")
    sp.add_argument("out")
    sp.set_defaults(fn=cmd_compare)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except query.FilterError as e:
        print(f"filter: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
