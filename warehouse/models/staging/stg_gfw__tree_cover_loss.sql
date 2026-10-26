-- warehouse/models/staging/stg_gfw__tree_cover_loss.sql
-- One row per district x threshold x year x primary x driver x protected category x plantation type.
select
    adm1::int                                              as adm1,
    adm2::int                                              as adm2,
    adm1::int * 1000 + adm2::int                           as district_id,
    umd_tree_cover_density_2000__threshold::int            as canopy_threshold,
    umd_tree_cover_loss__year::int                         as loss_year,
    coalesce(lower(is__umd_regional_primary_forest_2001) in ('true', 't', '1'), false)
                                                           as is_primary_forest,
    coalesce(nullif(trim(wri_google_tree_cover_loss_drivers__driver), ''), 'Unknown')
                                                           as driver_raw,
    nullif(trim(wdpa_protected_areas__iucn_cat), '')       as iucn_category,
    nullif(trim(wdpa_protected_areas__iucn_cat), '') is not null
                                                           as is_protected,
    nullif(trim(gfw_planted_forests__type), '')            as plantation_type,
    nullif(trim(gfw_planted_forests__type), '') is not null
                                                           as is_plantation,
    umd_tree_cover_loss__ha::numeric                       as loss_ha,
    coalesce(umd_tree_cover_loss_from_fires__ha::numeric, 0)
                                                           as fire_loss_ha,
    coalesce(gfw_gross_emissions_co2e_all_gases__mg::numeric, 0)
                                                           as emissions_t_co2e   -- 1 Mg = 1 tonne
from {{ source('raw', 'tcl_change') }}
