-- warehouse/models/marts/fct_fire_alerts.sql
-- Grain: district x ISO week x confidence x primary forest.
select
    district_id,
    week_start_date,
    alert_year                                as year,
    iso_week,
    extract(month from week_start_date)::int  as month,
    confidence,
    is_primary_forest,
    sum(alerts)                               as alerts
from {{ ref('stg_gfw__fire_alerts') }}
where canopy_threshold = {{ var('viirs_threshold') }}
group by 1, 2, 3, 4, 5, 6, 7
