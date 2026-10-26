-- warehouse/models/staging/stg_gadm__districts.sql
-- GADM ids look like IND.10.3_1: country.adm1.adm2_version.
with d as (
    select *, regexp_match(gid_2, '^[A-Z]{3}\.(\d+)\.(\d+)_\d+$') as m
    from {{ source('raw', 'boundaries') }}
    where gid_2 is not null
)
select distinct on (m[1]::int, m[2]::int)
    m[1]::int * 1000 + m[2]::int                           as district_id,
    m[1]::int                                              as adm1,
    m[2]::int                                              as adm2,
    gid_1,
    gid_2,
    trim(name_1)                                           as state,
    trim(name_2)                                           as district,
    engtype_2                                              as district_type,
    gfw_area__ha::numeric                                  as gadm_area_ha
from d
where m is not null
order by m[1]::int, m[2]::int
