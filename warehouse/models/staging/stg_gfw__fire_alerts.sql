-- warehouse/models/staging/stg_gfw__fire_alerts.sql
select
    adm1::int                                              as adm1,
    adm2::int                                              as adm2,
    adm1::int * 1000 + adm2::int                           as district_id,
    alert__year::int                                       as alert_year,
    alert__week::int                                       as iso_week,
    to_date(alert__year || '-' || lpad(alert__week, 2, '0'), 'IYYY-IW')
                                                           as week_start_date,
    lower(confidence__cat)                                 as confidence,
    umd_tree_cover_density_2000__threshold::int            as canopy_threshold,
    coalesce(lower(is__umd_regional_primary_forest_2001) in ('true', 't', '1'), false)
                                                           as is_primary_forest,
    alert__count::int                                      as alerts
from {{ source('raw', 'viirs_weekly') }}
