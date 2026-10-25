"""Pull each configured source to data/raw/<name>/<version>/<name>.csv and record it in a manifest."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from ledger.config import Settings, Source
from ledger.gfw import GFW, GFWError
from ledger.log import get_logger

log = get_logger(__name__)


def raw_path(settings: Settings, src: Source) -> Path:
    return settings.raw_dir / src.name / src.version / f"{src.name}.csv"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_manifest(settings: Settings) -> dict:
    p = settings.raw_dir / "manifest.json"
    return json.loads(p.read_text()) if p.exists() else {}


def write_manifest(settings: Settings, manifest: dict) -> None:
    p = settings.raw_dir / "manifest.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def download(client: GFW, settings: Settings, src: Source, dest: Path) -> tuple[int, list[str]]:
    """Write the source to dest. Returns (data rows, the SQL queries that were run).

    GFW answers 500 to very large queries, so thresholds are pulled 3 at a time and joined.
    """
    if "{thresholds}" not in src.sql_path.read_text():
        sql = src.sql(settings.country, ())
        return client.download_csv(src.dataset, src.version, sql, dest), [sql]
    ts = settings.extract_thresholds
    sqls, parts, rows = [], [], 0
    try:
        for i in range(0, len(ts), 3):
            part = dest.with_suffix(f".t{i}")
            sql = src.sql(settings.country, ts[i : i + 3])
            rows += client.download_csv(src.dataset, src.version, sql, part)
            sqls.append(sql)
            parts.append(part)
        tmp = dest.with_suffix(".part")
        header, out = None, []
        for part in parts:
            lines = part.read_bytes().splitlines(keepends=True)
            if not lines:
                continue
            if header is None:
                header = lines[0]
            elif lines[0] != header:
                raise GFWError(f"{part.name} has different columns from the first part")
            body = lines[1:]
            if out and not out[-1].endswith(b"\n"):
                out[-1] += b"\n"  # a part may end without a newline; keep rows apart
            if not out:
                out.append(header)
            out.extend(body)
        if out and not out[-1].endswith(b"\n"):
            out[-1] += b"\n"
        tmp.write_bytes(b"".join(out))
        tmp.replace(dest)
    finally:
        for part in parts:
            part.unlink(missing_ok=True)
    return rows, sqls


def pull(settings: Settings, names: list[str] | None = None, force: bool = False) -> dict:
    unknown = set(names or []) - set(settings.sources)
    if unknown:
        raise ValueError(f"unknown source(s) {sorted(unknown)}; choose from {list(settings.sources)}")
    client = GFW(settings.api, settings.gfw_api_key)
    manifest = read_manifest(settings)
    for name, src in settings.sources.items():
        if names and name not in names:
            continue
        dest = raw_path(settings, src)
        if dest.exists() and not force:
            log.info("skip_existing", source=name, version=src.version, path=str(dest))
            continue
        t0 = time.monotonic()
        log.info("pull_start", source=name, dataset=src.dataset, version=src.version)
        rows, sqls = download(client, settings, src, dest)
        entry = {
            "dataset": src.dataset,
            "version": src.version,
            "path": str(dest.relative_to(settings.data_dir)),
            "rows": rows,
            "bytes": dest.stat().st_size,
            "sha256": sha256(dest),
            "sql": sqls,
            "pulled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        manifest[name] = entry
        write_manifest(settings, manifest)
        log.info(
            "pull_done",
            source=name,
            rows=rows,
            mb=round(entry["bytes"] / 1e6, 2),
            seconds=round(time.monotonic() - t0, 1),
        )
        if rows == 0:
            log.warning("empty_pull", source=name, hint="check the iso code and the version")
    return manifest


def newer_versions(settings: Settings) -> dict[str, list[str]]:
    """For each source, list GFW versions newer than the pinned one."""
    from ledger.gfw import version_key

    client = GFW(settings.api, settings.gfw_api_key)
    out = {}
    for name, src in settings.sources.items():
        pinned = version_key(src.version)
        newer = [v for v in client.versions(src.dataset) if version_key(v) > pinned]
        out[name] = newer
        log.info(
            "versions", source=name, pinned=src.version, newer=newer, latest_tag=client.latest(src.dataset)
        )
    return out
