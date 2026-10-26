-- warehouse/models/marts/mart_state_gfw_vs_isfr.sql
-- Two definitions of "forest", side by side. They are not supposed to match; the gap is the finding.
with gfw as (
    select
        state,
        round(sum(land_area_ha) / 100, 1)        as gfw_land_area_km2,
        round(sum(tree_cover_2000_ha) / 100, 1)  as gfw_tree_cover_2000_km2,
        round(sum(tree_cover_2010_ha) / 100, 1)  as gfw_tree_cover_2010_km2
    from {{ ref('dim_district') }}
    group by 1
),
loss as (
    select d.state, round(sum(f.loss_ha) / 100, 1) as gfw_loss_2001_last_km2
    from {{ ref('fct_tree_cover_loss') }} f
    join {{ ref('dim_district') }} d using (district_id)
    group by 1
)
select
    g.state,
    i.state_isfr,
    g.gfw_land_area_km2,
    i.geographic_area_km2                                       as isfr_geographic_area_km2,
    g.gfw_tree_cover_2000_km2,
    g.gfw_tree_cover_2010_km2,
    l.gfw_loss_2001_last_km2,
    i.forest_cover_2021_km2                                     as isfr_forest_cover_2021_km2,
    i.forest_cover_2023_km2                                     as isfr_forest_cover_2023_km2,
    i.forest_cover_2023_km2 - i.forest_cover_2021_km2           as isfr_change_2021_2023_km2,
    round(100 * i.forest_cover_2023_km2 / nullif(i.geographic_area_km2, 0), 2)
                                                                as isfr_forest_pct,
    round(100 * g.gfw_tree_cover_2000_km2 / nullif(g.gfw_land_area_km2, 0), 2)
                                                                as gfw_tree_cover_2000_pct
from gfw g
left join loss l using (state)
left join {{ ref('isfr_2023_states') }} i on i.gadm_state = g.state
