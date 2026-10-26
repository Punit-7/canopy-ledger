-- warehouse/tests/assert_fact_total_matches_staging.sql
-- Catches rows lost or duplicated by joins: the fact must hold exactly the staging total.
with s as (
    select sum(loss_ha) as v from {{ ref('stg_gfw__tree_cover_loss') }}
    where canopy_threshold = {{ var('canopy_threshold') }}
),
f as (select sum(loss_ha) as v from {{ ref('fct_tree_cover_loss') }})
select s.v as staging_ha, f.v as fact_ha
from s, f
where abs(coalesce(s.v, 0) - coalesce(f.v, 0)) > 0.01
