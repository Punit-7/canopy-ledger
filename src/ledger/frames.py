"""Read the raw CSVs into pandas with short, consistent column names."""

from __future__ import annotations

import pandas as pd

from ledger.config import Settings
from ledger.extract import raw_path

RENAME = {
    "umd_tree_cover_density_2000__threshold": "threshold",
    "umd_tree_cover_loss__year": "year",
    "is__umd_regional_primary_forest_2001": "is_primary",
    "wri_google_tree_cover_loss_drivers__driver": "driver",
    "wdpa_protected_areas__iucn_cat": "iucn_cat",
    "gfw_planted_forests__type": "plantation_type",
    "umd_tree_cover_loss__ha": "loss_ha",
    "umd_tree_cover_loss_from_fires__ha": "fire_loss_ha",
    "gfw_gross_emissions_co2e_all_gases__Mg": "emissions_t",  # 1 Mg = 1 tonne
    "area__ha": "area_ha",
    "umd_tree_cover_extent_2000__ha": "extent2000_ha",
    "umd_tree_cover_extent_2010__ha": "extent2010_ha",
    "umd_tree_cover_gain__ha": "gain_ha",
    "alert__year": "year",
    "alert__week": "week",
    "confidence__cat": "confidence",
    "alert__count": "alerts",
}
BOOLS = ["is_primary"]


def _bool(s: pd.Series) -> pd.Series:
    return (
        s.astype("string")
        .str.lower()
        .map({"true": True, "t": True, "1": True, "false": False, "f": False, "0": False})
    )


def read_raw(settings: Settings, name: str) -> pd.DataFrame:
    return tidy(pd.read_csv(raw_path(settings, settings.sources[name]), low_memory=False))


def tidy(df: pd.DataFrame) -> pd.DataFrame:
    """Short names, real booleans, and is_protected / is_plantation flags."""
    df = df.rename(columns=RENAME)
    for c in BOOLS:
        if c in df:
            df[c] = _bool(df[c]).fillna(False).astype(bool)
    if "iucn_cat" in df:
        df["is_protected"] = df["iucn_cat"].notna()
    if "plantation_type" in df:
        df["is_plantation"] = df["plantation_type"].notna()
    return df


def districts(boundaries: pd.DataFrame) -> pd.DataFrame:
    """adm1/adm2 integer codes -> state and district names, parsed from GADM ids like IND.10.3_1."""
    b = boundaries[boundaries["gid_2"].notna()].copy()
    parts = b["gid_2"].str.extract(r"^[A-Z]{3}\.(\d+)\.(\d+)_\d+$")
    b["adm1"] = pd.to_numeric(parts[0], errors="coerce").astype("Int64")
    b["adm2"] = pd.to_numeric(parts[1], errors="coerce").astype("Int64")
    out = b.rename(columns={"name_1": "state", "name_2": "district", "gfw_area__ha": "gadm_area_ha"})
    out = out[["adm1", "adm2", "gid_1", "gid_2", "state", "district", "engtype_2", "gadm_area_ha"]]
    return out.drop_duplicates(["adm1", "adm2"]).sort_values(["adm1", "adm2"]).reset_index(drop=True)
