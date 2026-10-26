-- sql/analysis/01_national_trend.sql
-- Annual loss with a centred 3-year moving average and year-on-year change.
with y as (
    select year, sum(loss_ha) as loss_ha, sum(fire_loss_ha) as fire_loss_ha
    from marts.fct_tree_cover_loss
    group by year
)
select
    y.year,
    dy.method_era,
    round(y.loss_ha)                                                         as loss_ha,
    round(avg(y.loss_ha) over (order by y.year rows between 1 preceding and 1 following))
                                                                             as loss_ma3_ha,
    round(100 * (y.loss_ha / lag(y.loss_ha) over (order by y.year) - 1), 1)  as yoy_pct,
    round(100 * y.fire_loss_ha / nullif(y.loss_ha, 0), 1)                    as fire_share_pct,
    round(sum(y.loss_ha) over (order by y.year))                             as cumulative_ha
from y
join marts.dim_year dy using (year)
order by y.year;
