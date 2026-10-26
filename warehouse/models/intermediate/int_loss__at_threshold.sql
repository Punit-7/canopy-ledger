-- warehouse/models/intermediate/int_loss__at_threshold.sql
-- The one place the canopy threshold is applied. Everything downstream is at a single threshold,
-- so summing can never double count across thresholds.
select
    district_id,
    loss_year,
    driver_raw,
    is_primary_forest,
    is_protected,
    is_plantation,
    sum(loss_ha)            as loss_ha,
    sum(fire_loss_ha)       as fire_loss_ha,
    sum(emissions_t_co2e)   as emissions_t_co2e
from {{ ref('stg_gfw__tree_cover_loss') }}
where canopy_threshold = {{ var('canopy_threshold') }}
group by 1, 2, 3, 4, 5, 6
