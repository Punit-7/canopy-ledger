-- sql/analysis/03_pareto.sql
-- How many districts make up half, 80% and 90% of all loss?
with d as (
    select district_id, sum(loss_ha) as loss_ha
    from marts.fct_tree_cover_loss
    group by 1
    having sum(loss_ha) > 0   -- districts with rows but zero loss are not "with loss"
),
c as (
    select
        row_number() over (order by loss_ha desc)                            as n,
        100 * sum(loss_ha) over (order by loss_ha desc
                                 rows between unbounded preceding and current row)
            / sum(loss_ha) over ()                                           as cum_pct
    from d
)
select
    count(*)                                                                 as districts_with_loss,
    min(n) filter (where cum_pct >= 50)                                      as districts_for_50pct,
    min(n) filter (where cum_pct >= 80)                                      as districts_for_80pct,
    min(n) filter (where cum_pct >= 90)                                      as districts_for_90pct
from c;
