-- Annual tree cover loss by district, split by the dimensions we analyse.
-- Grain of the result: one row per district x threshold x year x primary x driver x protected x plantation.
SELECT
  iso, adm1, adm2,
  umd_tree_cover_density_2000__threshold,
  umd_tree_cover_loss__year,
  is__umd_regional_primary_forest_2001,
  wri_google_tree_cover_loss_drivers__driver,
  wdpa_protected_areas__iucn_cat,
  gfw_planted_forests__type,
  SUM(umd_tree_cover_loss__ha) AS umd_tree_cover_loss__ha,
  SUM(umd_tree_cover_loss_from_fires__ha) AS umd_tree_cover_loss_from_fires__ha,
  SUM("gfw_gross_emissions_co2e_all_gases__Mg") AS "gfw_gross_emissions_co2e_all_gases__Mg"
FROM data
WHERE iso = '{iso}'
  AND umd_tree_cover_density_2000__threshold IN ({thresholds})
GROUP BY
  iso, adm1, adm2,
  umd_tree_cover_density_2000__threshold,
  umd_tree_cover_loss__year,
  is__umd_regional_primary_forest_2001,
  wri_google_tree_cover_loss_drivers__driver,
  wdpa_protected_areas__iucn_cat,
  gfw_planted_forests__type
