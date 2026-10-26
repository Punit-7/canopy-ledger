"""Reusable questions for the exploration notebooks. Every function takes tidy frames from frames.py."""

from __future__ import annotations

import pandas as pd

METHOD_BREAKS = [2011, 2015]  # years where the UMD method or satellite inputs changed


def at_threshold(df: pd.DataFrame, t: int = 30) -> pd.DataFrame:
    """Always filter to one canopy threshold before summing. Summing across thresholds double counts."""
    return df[df["threshold"] == t]


def national_trend(chg: pd.DataFrame, t: int = 30) -> pd.DataFrame:
    """Loss, fire loss and emissions per year, with a 3-year average, year-on-year change and fire share."""
    y = at_threshold(chg, t).groupby("year")[["loss_ha", "fire_loss_ha", "emissions_t"]].sum()
    y["loss_ma3"] = y["loss_ha"].rolling(3, center=True).mean()
    y["yoy_pct"] = y["loss_ha"].pct_change() * 100
    y["fire_share_pct"] = 100 * y["fire_loss_ha"] / y["loss_ha"]
    return y


def period_compare(trend: pd.DataFrame, a: tuple[int, int], b: tuple[int, int]) -> pd.Series:
    """Mean annual loss in two periods. Keep both periods on the same side of a method break."""
    ma = trend.loc[a[0] : a[1], "loss_ha"].mean()
    mb = trend.loc[b[0] : b[1], "loss_ha"].mean()
    return pd.Series(
        {f"mean_{a[0]}_{a[1]}": ma, f"mean_{b[0]}_{b[1]}": mb, "change_pct": 100 * (mb - ma) / ma}
    )


def by_region(
    chg: pd.DataFrame,
    summ: pd.DataFrame,
    names: pd.DataFrame,
    level: str = "state",
    t: int = 30,
    years: tuple[int, int] | None = None,
) -> pd.DataFrame:
    """Loss, extent and loss rate by state or district."""
    keys = ["adm1"] if level == "state" else ["adm1", "adm2"]
    c = at_threshold(chg, t)
    if years:
        c = c[c["year"].between(*years)]
    loss = c.groupby(keys)[["loss_ha", "fire_loss_ha", "emissions_t"]].sum()
    ext = at_threshold(summ, t).groupby(keys)[["extent2000_ha", "area_ha"]].sum()
    out = loss.join(ext, how="outer").fillna(0).reset_index()
    label = names.drop_duplicates(keys)[keys + (["state"] if level == "state" else ["state", "district"])]
    out = out.merge(label, on=keys, how="left")
    out["loss_rate_pct"] = 100 * out["loss_ha"] / out["extent2000_ha"].where(out["extent2000_ha"] > 0)
    out["tree_cover_2000_pct"] = 100 * out["extent2000_ha"] / out["area_ha"].where(out["area_ha"] > 0)
    out["share_of_national_pct"] = 100 * out["loss_ha"] / out["loss_ha"].sum()
    return out.sort_values("loss_ha", ascending=False).reset_index(drop=True)


def pareto(region_table: pd.DataFrame) -> pd.DataFrame:
    """Cumulative share of loss: how few regions account for most of it?"""
    p = region_table.sort_values("loss_ha", ascending=False).reset_index(drop=True)
    p["rank"] = p.index + 1
    p["cum_share_pct"] = 100 * p["loss_ha"].cumsum() / p["loss_ha"].sum()
    return p


def regions_for_share(region_table: pd.DataFrame, share: float = 50.0) -> int:
    """How many top regions it takes to reach `share` percent of national loss."""
    p = pareto(region_table)
    return int((p["cum_share_pct"] < share).sum() + 1)


def driver_mix(chg: pd.DataFrame, t: int = 30, by: str | None = None) -> pd.DataFrame:
    """Share of loss hectares by dominant driver, nationally or per `by` column."""
    c = at_threshold(chg, t).assign(driver=lambda d: d["driver"].fillna("(no driver)"))
    keys = ([by] if by else []) + ["driver"]
    out = c.groupby(keys)["loss_ha"].sum().reset_index()
    total = out.groupby(by)["loss_ha"].transform("sum") if by else out["loss_ha"].sum()
    out["share_pct"] = 100 * out["loss_ha"] / total
    return out.sort_values(keys[:-1] + ["loss_ha"], ascending=[True] * (len(keys) - 1) + [False])


def threshold_sensitivity(chg: pd.DataFrame) -> pd.DataFrame:
    """Total loss at every canopy threshold. Shows how much the definition of 'tree' matters."""
    t = chg.groupby("threshold")["loss_ha"].sum().to_frame()
    t["vs_30_pct"] = 100 * t["loss_ha"] / t.loc[30, "loss_ha"] if 30 in t.index else None
    return t


def fire_seasonality(
    viirs: pd.DataFrame, confidence: str | None = "h", threshold: int | None = 30
) -> pd.DataFrame:
    """Alerts by calendar month (from ISO week) and year. Filter the threshold like loss."""
    v = viirs if confidence is None else viirs[viirs["confidence"] == confidence]
    if threshold is not None and "threshold" in v:
        v = v[v["threshold"] == threshold]
    d = v.assign(
        week_start=pd.to_datetime(
            v["year"].astype(str) + "-W" + v["week"].astype(str).str.zfill(2) + "-1",
            format="%G-W%V-%u",
            errors="coerce",
        )
    )
    d["month"] = d["week_start"].dt.month
    return d.pivot_table(index="month", columns="year", values="alerts", aggfunc="sum", fill_value=0)
