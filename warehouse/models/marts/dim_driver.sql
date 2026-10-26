-- warehouse/models/marts/dim_driver.sql
select
    row_number() over (order by sort_order)  as driver_id,
    driver_raw,
    driver,
    driver_group,
    counts_as_deforestation,
    sort_order
from {{ ref('driver_categories') }}
