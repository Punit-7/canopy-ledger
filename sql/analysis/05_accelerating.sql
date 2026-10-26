-- sql/analysis/05_accelerating.sql
-- Districts where loss in the last 5 years is well above the 5 years before. Both windows are 2015+.
with w as (
    select
        f.district_id,
        sum(f.loss_ha) filter (where f.year between 2021 and 2025) / 5.0     as recent_avg_ha,
        sum(f.loss_ha) filter (where f.year between 2016 and 2020) / 5.0     as prior_avg_ha
    from marts.fct_tree_cover_loss f
    group by 1
)
select
    dd.state,
    dd.district,
    round(w.prior_avg_ha)                                                    as prior_avg_ha,
    round(w.recent_avg_ha)                                                   as recent_avg_ha,
    round(100 * (w.recent_avg_ha / nullif(w.prior_avg_ha, 0) - 1), 1)        as change_pct
from w
join marts.dim_district dd using (district_id)
where w.recent_avg_ha >= 100            -- ignore tiny districts where % change is noise
  and w.recent_avg_ha > 1.25 * w.prior_avg_ha
order by w.recent_avg_ha - w.prior_avg_ha desc;
