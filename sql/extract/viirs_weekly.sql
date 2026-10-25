-- VIIRS fire alert counts by district and ISO week.
SELECT
  iso, adm1, adm2,
  alert__year, alert__week,
  confidence__cat,
  umd_tree_cover_density_2000__threshold,
  is__umd_regional_primary_forest_2001,
  SUM(alert__count) AS alert__count
FROM data
WHERE iso = '{iso}'
GROUP BY
  iso, adm1, adm2,
  alert__year, alert__week,
  confidence__cat,
  umd_tree_cover_density_2000__threshold,
  is__umd_regional_primary_forest_2001
