-- Tree cover extent and land area by district. No year: these are stocks, not flows.
SELECT
  iso, adm1, adm2,
  umd_tree_cover_density_2000__threshold,
  is__umd_regional_primary_forest_2001,
  wdpa_protected_areas__iucn_cat,
  gfw_planted_forests__type,
  SUM(area__ha) AS area__ha,
  SUM(umd_tree_cover_extent_2000__ha) AS umd_tree_cover_extent_2000__ha,
  SUM(umd_tree_cover_extent_2010__ha) AS umd_tree_cover_extent_2010__ha,
  SUM(umd_tree_cover_gain__ha) AS umd_tree_cover_gain__ha
FROM data
WHERE iso = '{iso}'
  AND umd_tree_cover_density_2000__threshold IN ({thresholds})
GROUP BY
  iso, adm1, adm2,
  umd_tree_cover_density_2000__threshold,
  is__umd_regional_primary_forest_2001,
  wdpa_protected_areas__iucn_cat,
  gfw_planted_forests__type
