-- warehouse/models/staging/stg_gfw__tree_cover_extent.sql
select
    adm1::int                                              as adm1,
    adm2::int                                              as adm2,
    adm1::int * 1000 + adm2::int                           as district_id,
    umd_tree_cover_density_2000__threshold::int            as canopy_threshold,
    coalesce(lower(is__umd_regional_primary_forest_2001) in ('true', 't', '1'), false)
                                                           as is_primary_forest,
    nullif(trim(wdpa_protected_areas__iucn_cat), '') is not null
                                                           as is_protected,
    nullif(trim(gfw_planted_forests__type), '') is not null
                                                           as is_plantation,
    coalesce(area__ha::numeric, 0)                         as area_ha,
    coalesce(umd_tree_cover_extent_2000__ha::numeric, 0)   as extent_2000_ha,
    coalesce(umd_tree_cover_extent_2010__ha::numeric, 0)   as extent_2010_ha,
    coalesce(umd_tree_cover_gain__ha::numeric, 0)          as gain_ha
from {{ source('raw', 'tcl_summary') }}
