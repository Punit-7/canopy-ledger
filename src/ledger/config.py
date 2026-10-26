# src/ledger/config.py
"""Settings come from two places: secrets from .env, everything else from configs/sources.toml."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Source:
    name: str
    dataset: str
    version: str
    sql_path: Path

    def sql(self, iso: str, thresholds: tuple[int, ...]) -> str:
        text = self.sql_path.read_text().replace("{iso}", iso)
        return text.replace("{thresholds}", ", ".join(str(t) for t in thresholds))


@dataclass(frozen=True)
class Settings:
    gfw_api_key: str
    database_url: str
    data_dir: Path
    log_level: str
    log_json: bool
    country: str
    api: str
    expect_max_loss_year: int
    canopy_threshold: int
    extract_thresholds: tuple[int, ...]
    sources: dict[str, Source]

    @property
    def raw_dir(self) -> Path:
        return self.data_dir / "raw"


def load_settings(config: Path | None = None) -> Settings:
    load_dotenv(ROOT / ".env")
    cfg = tomllib.loads((config or ROOT / "configs" / "sources.toml").read_text())
    sources = {
        name: Source(name, s["dataset"], s["version"], ROOT / s["sql"]) for name, s in cfg["sources"].items()
    }
    return Settings(
        gfw_api_key=os.environ.get("GFW_API_KEY", ""),
        database_url=os.environ.get("DATABASE_URL", ""),
        data_dir=(ROOT / os.environ.get("DATA_DIR", "data")).resolve(),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
        log_json=os.environ.get("LOG_JSON", "true").lower() == "true",
        country=cfg["country"],
        api=cfg["api"],
        expect_max_loss_year=int(cfg["expect_max_loss_year"]),
        canopy_threshold=int(cfg["canopy_threshold"]),
        extract_thresholds=tuple(
            int(t) for t in os.environ.get("EXTRACT_THRESHOLDS", "10,15,20,25,30,50,75").split(",")
        ),
        sources=sources,
    )
