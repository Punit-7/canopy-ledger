-- warehouse/tests/assert_every_year_present.sql
select y.year
from {{ ref('dim_year') }} y
left join (select distinct year from {{ ref('fct_tree_cover_loss') }}) f using (year)
where f.year is null
