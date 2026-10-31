# tests/test_explore.py
import pytest

from ledger import explore as ex


def test_trend_uses_one_threshold(frames):
    chg = frames["chg"]
    trend = ex.national_trend(chg, t=30)
    expected = chg[(chg.threshold == 30) & (chg.year == 2010)]["loss_ha"].sum()
    assert trend.loc[2010, "loss_ha"] == pytest.approx(expected)
    # summing every threshold would be several times bigger: the trap this guards against
    assert chg[chg.year == 2010]["loss_ha"].sum() > 5 * expected


def test_region_shares_add_up(frames):
    t = ex.by_region(frames["chg"], frames["summ"], frames["names"], "district")
    assert t["share_of_national_pct"].sum() == pytest.approx(100)
    assert t["district"].notna().all()


def test_pareto_ends_at_100(frames):
    t = ex.by_region(frames["chg"], frames["summ"], frames["names"], "district")
    p = ex.pareto(t)
    assert p["cum_share_pct"].iloc[-1] == pytest.approx(100)
    assert 1 <= ex.regions_for_share(t, 50) <= len(t)


def test_fire_months(frames):
    m = ex.fire_seasonality(frames["viirs"])
    assert set(m.index) <= set(range(1, 13))
    assert m.loc[3].sum() > m.loc[8].sum()  # fixture peaks in March
