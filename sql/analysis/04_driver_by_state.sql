-- sql/analysis/04_driver_by_state.sql
-- Driver mix per state, as a share of that state's loss. Top 10 states only.
with s as (
    select dd.state, dr.driver, sum(f.loss_ha) as loss_ha
    from marts.fct_tree_cover_loss f
    join marts.dim_district dd using (district_id)
    join marts.dim_driver dr using (driver_id)
    group by 1, 2
),
top as (
    select state from s group by state order by sum(loss_ha) desc limit 10
)
select
    s.state,
    s.driver,
    round(s.loss_ha)                                                         as loss_ha,
    round(100 * s.loss_ha / sum(s.loss_ha) over (partition by s.state), 1)   as share_of_state_pct
from s
join top using (state)
order by sum(s.loss_ha) over (partition by s.state) desc, s.loss_ha desc;
