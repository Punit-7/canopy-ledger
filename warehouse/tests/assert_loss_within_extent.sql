-- warehouse/tests/assert_loss_within_extent.sql
-- Loss can land on trees that grew after 2000, so a small overshoot is possible. A big one is a bug.
{{ config(severity='warn') }}
select d.state_district, d.tree_cover_2000_ha, sum(f.loss_ha) as loss_ha
from {{ ref('fct_tree_cover_loss') }} f
join {{ ref('dim_district') }} d using (district_id)
group by 1, 2
having sum(f.loss_ha) > 1.05 * d.tree_cover_2000_ha + 1
