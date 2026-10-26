-- sql/analysis/02_top_districts.sql
-- Top districts by loss since 2015 (current method era), ranked nationally and within their state.
with d as (
    select f.district_id, sum(f.loss_ha) as loss_ha
    from marts.fct_tree_cover_loss f
    join marts.dim_year y using (year)
    where y.is_comparable_era
    group by 1
)
select
    rank() over (order by d.loss_ha desc)                                    as national_rank,
    rank() over (partition by dd.state order by d.loss_ha desc)              as rank_in_state,
    dd.state,
    dd.district,
    round(d.loss_ha)                                                         as loss_ha,
    round(100 * d.loss_ha / nullif(dd.tree_cover_2000_ha, 0), 2)             as loss_rate_pct,
    round(100 * d.loss_ha / sum(d.loss_ha) over (), 2)                       as share_pct
from d
join marts.dim_district dd using (district_id)
order by national_rank
limit 25;
