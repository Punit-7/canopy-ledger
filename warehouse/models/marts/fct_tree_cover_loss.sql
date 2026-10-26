-- warehouse/models/marts/fct_tree_cover_loss.sql
-- Grain: district x year x driver x primary forest x protected x plantation, at one canopy threshold.
select
    l.district_id,
    l.loss_year                       as year,
    d.driver_id,
    l.is_primary_forest,
    l.is_protected,
    l.is_plantation,
    (d.counts_as_deforestation = 'always'
        or (d.counts_as_deforestation = 'in primary forest only' and l.is_primary_forest))
                                      as is_deforestation,
    l.loss_ha,
    l.fire_loss_ha,
    l.emissions_t_co2e
from {{ ref('int_loss__at_threshold') }} l
join {{ ref('dim_driver') }} d using (driver_raw)
