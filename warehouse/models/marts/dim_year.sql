-- warehouse/models/marts/dim_year.sql
-- Years with the method era each falls in, so reports can warn when a comparison crosses one.
select
    y                                                                   as year,
    make_date(y, 1, 1)                                                  as year_start,
    case
        when y <= 2010 then '2001-2010 original method'
        when y <= 2014 then '2011-2014 updated method'
        else '2015+ current method'
    end                                                                 as method_era,
    (y >= 2015)                                                         as is_comparable_era,
    (y > {{ var('last_loss_year') }} - 5)                               as is_last_5_years
from generate_series({{ var('first_loss_year') }}, {{ var('last_loss_year') }}) as y
