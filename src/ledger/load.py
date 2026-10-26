"""Load raw CSVs into PostgreSQL as text columns. dbt does all typing and cleaning after this."""

from __future__ import annotations

import csv
import time
from pathlib import Path

import psycopg
from psycopg import sql

from ledger.config import Settings
from ledger.extract import raw_path, read_manifest
from ledger.log import get_logger

log = get_logger(__name__)

LOADS_DDL = """
create schema if not exists raw;
create table if not exists raw._loads (
    source      text not null,
    dataset     text not null,
    version     text not null,
    sha256      text not null,
    rows        bigint not null,
    loaded_at   timestamptz not null default now(),
    primary key (source, sha256)
);
"""


def load_csv(conn: psycopg.Connection, table: str, path: Path) -> int:
    with path.open(newline="") as f:
        header = next(csv.reader(f))
    cols = [c.strip().lower() for c in header]
    ident = sql.Identifier("raw", table)
    with conn.cursor() as cur:
        cur.execute(sql.SQL("drop table if exists {}").format(ident))
        cur.execute(
            sql.SQL("create table {} ({})").format(
                ident, sql.SQL(", ").join(sql.SQL("{} text").format(sql.Identifier(c)) for c in cols)
            )
        )
        copy_sql = sql.SQL("copy {} ({}) from stdin with (format csv, header true)").format(
            ident, sql.SQL(", ").join(map(sql.Identifier, cols))
        )
        with path.open("rb") as f, cur.copy(copy_sql) as copy:
            while block := f.read(1 << 20):
                copy.write(block)
        cur.execute(sql.SQL("select count(*) from {}").format(ident))
        return cur.fetchone()[0]


def load_all(s: Settings, names: list[str] | None = None) -> None:
    manifest = read_manifest(s)
    with psycopg.connect(s.database_url) as conn:
        conn.execute(LOADS_DDL)
        for name, src in s.sources.items():
            if names and name not in names:
                continue
            entry = manifest.get(name)
            if not entry or entry["version"] != src.version:
                raise RuntimeError(f"{name}: no pull for pinned version {src.version}; run extract")
            t0 = time.monotonic()
            rows = load_csv(conn, name, raw_path(s, src))
            if rows != entry["rows"]:
                raise RuntimeError(f"{name}: loaded {rows} rows, manifest says {entry['rows']}")
            conn.execute(
                "insert into raw._loads (source, dataset, version, sha256, rows) "
                "values (%s, %s, %s, %s, %s) on conflict (source, sha256) do update "
                "set loaded_at = now()",
                (name, src.dataset, src.version, entry["sha256"], rows),
            )
            conn.commit()
            log.info(
                "loaded", source=name, table=f"raw.{name}", rows=rows, seconds=round(time.monotonic() - t0, 1)
            )
