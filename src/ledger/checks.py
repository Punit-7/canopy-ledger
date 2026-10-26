"""Data quality checks on the raw pulls. Each check returns a Result; the CLI fails if any 'error' fails."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise

import pandas as pd

from ledger.config import Settings
from ledger.frames import districts, read_raw
from ledger.log import get_logger

log = get_logger(__name__)

CHANGE_KEY = ["adm1", "adm2", "threshold", "year", "is_primary", "driver", "iucn_cat", "plantation_type"]


@dataclass
class Result:
    name: str
    passed: bool
    severity: str  # "error" stops the pipeline, "warn" is logged
    detail: str


def _r(name: str, ok: bool, detail: str, severity: str = "error") -> Result:
    return Result(name, bool(ok), severity, detail)


def check_change(chg: pd.DataFrame, s: Settings) -> list[Result]:
    out = []
    dup = chg.duplicated(CHANGE_KEY, keep=False).sum()
    out.append(_r("change.unique_grain", dup == 0, f"{dup} rows share a key"))

    years = sorted(int(y) for y in chg["year"].dropna().unique())
    out.append(
        _r(
            "change.max_year",
            years and years[-1] == s.expect_max_loss_year,
            f"max year {years[-1] if years else None}, expected {s.expect_max_loss_year}",
        )
    )
    missing = sorted(set(range(2001, s.expect_max_loss_year + 1)) - set(years))
    out.append(_r("change.no_missing_years", not missing, f"missing years: {missing}"))

    thresholds = sorted(int(t) for t in chg["threshold"].unique())
    out.append(
        _r("change.has_threshold", s.canopy_threshold in thresholds, f"thresholds present: {thresholds}")
    )

    neg = (chg[["loss_ha", "fire_loss_ha", "emissions_t"]] < 0).any(axis=1).sum()
    out.append(_r("change.non_negative", neg == 0, f"{neg} rows with negative measures"))

    over = (chg["fire_loss_ha"] > chg["loss_ha"] * 1.0001 + 1e-6).sum()
    out.append(_r("change.fire_le_loss", over == 0, f"{over} rows where fire loss > total loss"))

    # Loss at a higher canopy threshold is a subset of loss at a lower one.
    by_t = chg.groupby(["adm1", "adm2", "year", "threshold"])["loss_ha"].sum().unstack("threshold")
    cols = sorted(by_t.columns)
    breaks = sum(int((by_t[a] + 1e-6 < by_t[b]).sum()) for a, b in pairwise(cols))
    out.append(
        _r(
            "change.threshold_monotonic",
            breaks == 0,
            f"{breaks} district-years where loss rises with a stricter threshold",
            "warn",
        )
    )
    return out


def check_extent(chg: pd.DataFrame, summ: pd.DataFrame, s: Settings) -> list[Result]:
    t = s.canopy_threshold
    loss = chg[chg.threshold == t].groupby(["adm1", "adm2"])["loss_ha"].sum()
    ext = summ[summ.threshold == t].groupby(["adm1", "adm2"])["extent2000_ha"].sum()
    j = pd.concat([loss, ext], axis=1).fillna(0)
    bad = j[j.loss_ha > j.extent2000_ha * 1.05 + 1]
    return [
        _r(
            "extent.loss_le_extent",
            bad.empty,
            f"{len(bad)} districts lost more than 105% of their 2000 extent",
            "warn",
        )
    ]


def check_names(chg: pd.DataFrame, names: pd.DataFrame) -> list[Result]:
    keys = chg[["adm1", "adm2"]].drop_duplicates()
    m = keys.merge(names, on=["adm1", "adm2"], how="left", indicator=True)
    orphans = m[m["_merge"] == "left_only"]
    sample = orphans[["adm1", "adm2"]].head(5).to_dict("records")
    return [
        _r(
            "names.every_district_named",
            orphans.empty,
            f"{len(orphans)} adm1/adm2 codes without a name, e.g. {sample}",
        )
    ]


def check_reference(
    chg: pd.DataFrame,
    s: Settings,
    reference_ha: float | None,
    first: int = 2001,
    last: int | None = None,
    tol: float = 0.01,
) -> list[Result]:
    """Compare the national total with the figure on the GFW country dashboard."""
    if reference_ha is None:
        return []
    last = last or s.expect_max_loss_year
    sub = chg[(chg.threshold == s.canopy_threshold) & chg.year.between(first, last)]
    total = sub["loss_ha"].sum()
    diff = abs(total - reference_ha) / reference_ha
    return [
        _r(
            "reference.national_total",
            diff <= tol,
            f"{total:,.0f} ha vs dashboard {reference_ha:,.0f} ha ({diff:.2%} apart)",
        )
    ]


def run_all(s: Settings, reference_ha: float | None = None) -> list[Result]:
    chg = read_raw(s, "tcl_change")
    summ = read_raw(s, "tcl_summary")
    names = districts(read_raw(s, "boundaries"))
    results = (
        check_change(chg, s)
        + check_extent(chg, summ, s)
        + check_names(chg, names)
        + check_reference(chg, s, reference_ha)
    )
    for r in results:
        level = log.info if r.passed else (log.error if r.severity == "error" else log.warning)
        level("check", name=r.name, passed=r.passed, severity=r.severity, detail=r.detail)
    return results
