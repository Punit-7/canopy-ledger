"""Small synthetic files with the same columns as the real pulls, for tests and CI.

The numbers are random. Never analyse them; they only exist so the pipeline can run without the API.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

THRESHOLDS = [10, 15, 20, 25, 30, 50, 75]
DRIVERS = [
    "Permanent agriculture",
    "Hard commodities",
    "Shifting cultivation",
    "Logging",
    "Wildfire",
    "Settlements and infrastructure",
    "Other natural disturbances",
]
DISTRICTS = [
    (1, 1, "Assam", "Karbi Anglong"),
    (1, 2, "Assam", "Dima Hasao"),
    (2, 1, "Mizoram", "Lunglei"),
    (2, 2, "Mizoram", "Mamit"),
    (3, 1, "Odisha", "Kandhamal"),
]


def _shrink(t: int) -> float:
    return {10: 1.25, 15: 1.18, 20: 1.1, 25: 1.05, 30: 1.0, 50: 0.8, 75: 0.45}[t]


def make_frames(iso: str = "IND", last_year: int = 2025, seed: int = 7) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    rows = []
    for (a1, a2, _, _), year, primary, driver in itertools.product(
        DISTRICTS, range(2001, last_year + 1), [False, True], DRIVERS
    ):
        base = rng.gamma(2.0, 40.0) * (1.6 if driver == "Shifting cultivation" else 1.0)
        prot = rng.random() < 0.2
        for t in THRESHOLDS:
            loss = round(base * _shrink(t), 3)
            rows.append(
                {
                    "iso": iso,
                    "adm1": a1,
                    "adm2": a2,
                    "umd_tree_cover_density_2000__threshold": t,
                    "umd_tree_cover_loss__year": year,
                    "is__umd_regional_primary_forest_2001": str(primary).lower(),
                    "wri_google_tree_cover_loss_drivers__driver": driver,
                    "wdpa_protected_areas__iucn_cat": "II" if prot else None,
                    "gfw_planted_forests__type": None,
                    "umd_tree_cover_loss__ha": loss,
                    "umd_tree_cover_loss_from_fires__ha": round(loss * rng.uniform(0, 0.1), 3),
                    "gfw_gross_emissions_co2e_all_gases__Mg": round(loss * rng.uniform(150, 400), 1),
                }
            )
    change = pd.DataFrame(rows)

    summ = []
    for (a1, a2, _, _), primary in itertools.product(DISTRICTS, [False, True]):
        area = rng.uniform(2e5, 6e5)
        ext30 = area * rng.uniform(0.3, 0.7)
        for t in THRESHOLDS:
            summ.append(
                {
                    "iso": iso,
                    "adm1": a1,
                    "adm2": a2,
                    "umd_tree_cover_density_2000__threshold": t,
                    "is__umd_regional_primary_forest_2001": str(primary).lower(),
                    "wdpa_protected_areas__iucn_cat": None,
                    "gfw_planted_forests__type": None,
                    "area__ha": round(area, 1),
                    "umd_tree_cover_extent_2000__ha": round(ext30 * _shrink(t), 1),
                    "umd_tree_cover_extent_2010__ha": round(ext30 * _shrink(t) * 0.97, 1),
                    "umd_tree_cover_gain__ha": round(ext30 * 0.01, 1),
                }
            )
    summary = pd.DataFrame(summ)

    v = []
    for (a1, a2, _, _), year, week, conf in itertools.product(
        DISTRICTS, range(2012, last_year + 1), range(1, 53), ["h", "n", "l"]
    ):
        peak = 30 * np.exp(-((week - 12) ** 2) / 30)  # dry-season peak around March
        v.append(
            {
                "iso": iso,
                "adm1": a1,
                "adm2": a2,
                "alert__year": year,
                "alert__week": week,
                "confidence__cat": conf,
                "umd_tree_cover_density_2000__threshold": 30,
                "is__umd_regional_primary_forest_2001": "false",
                "alert__count": int(rng.poisson(peak + 1)),
            }
        )
    viirs = pd.DataFrame(v)

    b = [
        {
            "gid_0": iso,
            "gid_1": f"{iso}.{a1}_1",
            "name_1": st,
            "gid_2": f"{iso}.{a1}.{a2}_1",
            "name_2": dist,
            "type_2": "District",
            "engtype_2": "District",
            "adm_level": "2",
            "gfw_area__ha": 4e5,
        }
        for a1, a2, st, dist in DISTRICTS
    ]
    boundaries = pd.DataFrame(b)

    return {"tcl_change": change, "tcl_summary": summary, "viirs_weekly": viirs, "boundaries": boundaries}


def install(settings) -> None:
    """Write fixtures where `extract` would have put real pulls, with a matching manifest."""
    from ledger.extract import raw_path, read_manifest, sha256, write_manifest

    manifest = read_manifest(settings)
    frames = make_frames(settings.country, settings.expect_max_loss_year)
    for name, src in settings.sources.items():
        dest = raw_path(settings, src)
        dest.parent.mkdir(parents=True, exist_ok=True)
        frames[name].to_csv(dest, index=False)
        manifest[name] = {
            "dataset": src.dataset,
            "version": src.version,
            "path": str(dest.relative_to(settings.data_dir)),
            "rows": len(frames[name]),
            "bytes": dest.stat().st_size,
            "sha256": sha256(dest),
            "sql": "fixture",
            "pulled_at": "fixture",
        }
    write_manifest(settings, manifest)
