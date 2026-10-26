-- warehouse/tests/assert_loss_grain_unique.sql
-- Returns rows (= fails) if the fact table has two rows for the same grain.
select district_id, year, driver_id, is_primary_forest, is_protected, is_plantation, count(*)
from {{ ref('fct_tree_cover_loss') }}
group by 1, 2, 3, 4, 5, 6
having count(*) > 1
