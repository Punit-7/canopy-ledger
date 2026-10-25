"""A small client for the Global Forest Watch Data API."""

from __future__ import annotations

import re
import time
from pathlib import Path

import requests

from ledger.log import get_logger

log = get_logger(__name__)


def version_key(version: str) -> tuple:
    """Sort GFW version strings: v202204 < v202204.2 < v20250515 < v20260424.

    Month-only versions (6 digits) are padded to the first of the month so they compare with
    day versions. Non-date versions like v4.1 sort by their numbers.
    """
    m = re.fullmatch(r"v(\d+)(?:\.(\d+))?", version)
    if not m:
        return (0, version)
    main, minor = m.group(1), int(m.group(2) or 0)
    if len(main) == 6:
        main += "01"
    return (int(main), minor)


class GFWError(RuntimeError):
    pass


class GFW:
    def __init__(self, api: str, api_key: str = "", timeout: int = 600, retries: int = 4):
        self.api = api.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers["User-Agent"] = "canopy-ledger/0.1"
        if api_key:
            self.session.headers["x-api-key"] = api_key

    def _get(self, path: str, stream: bool = False, **params) -> requests.Response:
        url = f"{self.api}{path}"
        for attempt in range(1, self.retries + 1):
            try:
                r = self.session.get(url, params=params, timeout=self.timeout, stream=stream)
            except requests.ConnectionError as e:
                err = str(e)
            else:
                if r.status_code < 400:
                    return r
                err = f"HTTP {r.status_code}: {r.text[:500]}"
                if r.status_code < 500 and r.status_code != 429:
                    raise GFWError(f"{path} -> {err}")
            wait = 2**attempt
            log.warning("gfw_retry", path=path, attempt=attempt, wait_s=wait, error=err)
            time.sleep(wait)
        raise GFWError(f"{path} failed after {self.retries} attempts: {err}")

    def versions(self, dataset: str) -> list[str]:
        data = self._get(f"/dataset/{dataset}").json()["data"]
        return sorted(data["versions"], key=version_key)

    def latest(self, dataset: str) -> str:
        """The version GFW has tagged as latest. Can lag behind the newest version."""
        return self._get(f"/dataset/{dataset}/latest").json()["data"]["version"]

    def fields(self, dataset: str, version: str) -> list[dict]:
        return self._get(f"/dataset/{dataset}/{version}/fields").json()["data"]

    def query_json(self, dataset: str, version: str, sql: str) -> list[dict]:
        return self._get(f"/dataset/{dataset}/{version}/query/json", sql=sql).json()["data"]

    def download_csv(self, dataset: str, version: str, sql: str, dest: Path) -> int:
        """Stream a query result to a CSV file. Returns the number of data rows."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(".part")
        r = self._get(f"/dataset/{dataset}/{version}/download/csv", stream=True, sql=sql)
        newlines, last = 0, b"\n"
        with tmp.open("wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                newlines += chunk.count(b"\n")
                last = chunk[-1:] or last
        lines = newlines + (0 if last == b"\n" else 1)
        tmp.replace(dest)
        return max(lines - 1, 0)
