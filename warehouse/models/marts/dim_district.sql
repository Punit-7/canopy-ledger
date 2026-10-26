-- warehouse/models/marts/dim_district.sql
-- One row per district, with the stock figures that loss rates are divided by.
with extent as (
    select
        district_id,
        sum(area_ha)                                                   as land_area_ha,
        sum(extent_2000_ha)                                            as tree_cover_2000_ha,
        sum(extent_2010_ha)                                            as tree_cover_2010_ha,
        sum(extent_2000_ha) filter (where is_primary_forest)           as primary_forest_2001_ha,
        sum(extent_2000_ha) filter (where is_protected)                as protected_tree_cover_2000_ha
    from {{ ref('stg_gfw__tree_cover_extent') }}
    where canopy_threshold = {{ var('canopy_threshold') }}
    group by 1
)
select
    d.district_id,
    d.adm1,
    d.adm2,
    d.gid_2,
    d.state,
    d.district,
    d.state || ' / ' || d.district                                     as state_district,
    d.district_type,
    coalesce(e.land_area_ha, 0)                                        as land_area_ha,
    coalesce(e.tree_cover_2000_ha, 0)                                  as tree_cover_2000_ha,
    coalesce(e.tree_cover_2010_ha, 0)                                  as tree_cover_2010_ha,
    coalesce(e.primary_forest_2001_ha, 0)                              as primary_forest_2001_ha,
    coalesce(e.protected_tree_cover_2000_ha, 0)                        as protected_tree_cover_2000_ha,
    round(100 * e.tree_cover_2000_ha / nullif(e.land_area_ha, 0), 2)   as tree_cover_2000_pct
from {{ ref('stg_gadm__districts') }} d
left join extent e using (district_id)
