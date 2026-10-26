import pandas as pd

from ledger.checks import check_change, check_extent, check_names


def by_name(results):
    return {r.name: r for r in results}


def test_clean_fixture_passes(frames, settings):
    results = (
        check_change(frames["chg"], settings)
        + check_extent(frames["chg"], frames["summ"], settings)
        + check_names(frames["chg"], frames["names"])
    )
    assert all(r.passed for r in results), [r for r in results if not r.passed]


def test_duplicate_rows_are_caught(frames, settings):
    chg = frames["chg"]
    broken = pd.concat([chg, chg.iloc[[0]]], ignore_index=True)
    assert not by_name(check_change(broken, settings))["change.unique_grain"].passed


def test_fire_above_total_is_caught(frames, settings):
    broken = frames["chg"].copy()
    broken.loc[0, "fire_loss_ha"] = broken.loc[0, "loss_ha"] + 5
    assert not by_name(check_change(broken, settings))["change.fire_le_loss"].passed


def test_missing_year_is_caught(frames, settings):
    broken = frames["chg"][frames["chg"]["year"] != 2013]
    assert not by_name(check_change(broken, settings))["change.no_missing_years"].passed


def test_unnamed_district_is_caught(frames):
    names = frames["names"].iloc[1:]
    assert not check_names(frames["chg"], names)[0].passed
