# src/ledger/cli.py
"""The `ledger` command. Every step of the pipeline is one subcommand."""

from __future__ import annotations

import argparse
import json
import sys

from ledger import log as logmod
from ledger.config import load_settings

log = logmod.get_logger("ledger.cli")


def cmd_versions(s, args) -> int:
    from ledger.gfw import GFW

    client = GFW(s.api, s.gfw_api_key)
    for name, src in s.sources.items():
        versions = client.versions(src.dataset)
        print(f"{name:14} {src.dataset}")
        print(f"{'':14} pinned={src.version}  latest_tag={client.latest(src.dataset)}")
        print(f"{'':14} newest five: {', '.join(versions[-5:])}")
    return 0


def cmd_fields(s, args) -> int:
    from ledger.gfw import GFW

    src = s.sources[args.source]
    for f in GFW(s.api, s.gfw_api_key).fields(src.dataset, args.version or src.version):
        print(f"{f.get('name') or f.get('pixel_meaning'):55} {f.get('data_type', '')}")
    return 0


def cmd_sql(s, args) -> int:
    from ledger.gfw import GFW

    src = s.sources[args.source]
    rows = GFW(s.api, s.gfw_api_key).query_json(src.dataset, args.version or src.version, args.sql)
    print(json.dumps(rows, indent=2, default=str))
    return 0


def cmd_extract(s, args) -> int:
    from ledger.extract import pull

    pull(s, args.only or None, force=args.force)
    return 0


def cmd_check_versions(s, args) -> int:
    from ledger.extract import newer_versions

    newer = {k: v for k, v in newer_versions(s).items() if v}
    if newer:
        log.warning("newer_versions_available", **newer)
        return 3 if args.strict else 0
    return 0


def cmd_profile(s, args) -> int:
    from ledger.config import ROOT
    from ledger.frames import read_raw
    from ledger.profile import report

    out = ROOT / "docs" / "profiles"
    out.mkdir(parents=True, exist_ok=True)
    for name in args.only or list(s.sources):
        df = read_raw(s, name)
        (out / f"{name}.md").write_text(report(name, df))
        log.info("profiled", source=name, rows=len(df), path=str(out / f"{name}.md"))
    return 0


def cmd_checks(s, args) -> int:
    from ledger.checks import run_all

    results = run_all(s, reference_ha=args.reference_ha)
    failed = [r for r in results if not r.passed and r.severity == "error"]
    print(
        f"{len(results)} checks, {len(failed)} errors, "
        f"{sum(not r.passed and r.severity == 'warn' for r in results)} warnings"
    )
    return 1 if failed else 0


def cmd_load(s, args) -> int:
    from ledger.load import load_all

    load_all(s, args.only or None)
    return 0


def cmd_fixtures(s, args) -> int:
    from ledger.fixtures import install

    install(s)
    log.info("fixtures_installed", data_dir=str(s.data_dir))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="ledger", description="Canopy Ledger data pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("versions", help="list GFW versions for each source")
    f = sub.add_parser("fields", help="list the fields of a source")
    f.add_argument("source")
    f.add_argument("--version")
    q = sub.add_parser("sql", help="run a small SQL query against a source (JSON out)")
    q.add_argument("source")
    q.add_argument("sql")
    q.add_argument("--version")
    e = sub.add_parser("extract", help="pull pinned versions to data/raw")
    e.add_argument("--only", nargs="*")
    e.add_argument("--force", action="store_true")
    cv = sub.add_parser("check-versions", help="warn if GFW has newer versions than pinned")
    cv.add_argument("--strict", action="store_true", help="exit 3 when newer versions exist")
    pr = sub.add_parser("profile", help="write docs/profiles/<source>.md")
    pr.add_argument("--only", nargs="*")
    c = sub.add_parser("checks", help="data quality checks on the raw pulls")
    c.add_argument("--reference-ha", type=float, help="national loss from the GFW dashboard")
    ld = sub.add_parser("load", help="load raw CSVs into PostgreSQL")
    ld.add_argument("--only", nargs="*")
    sub.add_parser("fixtures", help="write synthetic raw files (tests and CI only)")

    args = p.parse_args(argv)
    s = load_settings()
    logmod.setup(s.log_level, s.log_json)
    handler = globals()[f"cmd_{args.cmd.replace('-', '_')}"]
    try:
        return handler(s, args)
    except Exception:
        log.exception("command_failed", cmd=args.cmd)
        return 1


if __name__ == "__main__":
    sys.exit(main())
