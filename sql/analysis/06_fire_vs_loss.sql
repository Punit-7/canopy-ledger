-- sql/analysis/06_fire_vs_loss.sql
-- Do districts with more high-confidence fire alerts lose more tree cover to fire? (2012+ only.)
with a as (
    select district_id, year, sum(alerts) as alerts
    from marts.fct_fire_alerts
    where confidence = 'h'
    group by 1, 2
),
l as (
    select district_id, year, sum(fire_loss_ha) as fire_loss_ha, sum(loss_ha) as loss_ha
    from marts.fct_tree_cover_loss
    where year >= 2012
    group by 1, 2
)
select
    count(*)                                                                 as district_years,
    round(corr(a.alerts, l.fire_loss_ha)::numeric, 3)                        as r_alerts_vs_fire_loss,
    round(corr(a.alerts, l.loss_ha)::numeric, 3)                             as r_alerts_vs_all_loss
from a
join l using (district_id, year);
