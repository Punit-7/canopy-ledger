-- warehouse/tests/assert_fire_loss_within_loss.sql
select *
from {{ ref('fct_tree_cover_loss') }}
where fire_loss_ha > loss_ha + 0.001
