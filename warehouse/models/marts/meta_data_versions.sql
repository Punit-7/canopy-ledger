-- warehouse/models/marts/meta_data_versions.sql
-- Which GFW version is in the warehouse right now. The report footer reads this.
select distinct on (source)
    source,
    dataset,
    version,
    rows,
    loaded_at
from {{ source('raw', '_loads') }}
order by source, loaded_at desc
