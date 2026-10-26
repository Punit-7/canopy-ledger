# docs/data_dictionary.md

| Field | Meaning | Notes |
|---|---|---|
| iso, adm1, adm2 | Country code, state code, district code (GADM integer ids) | Codes, not names. Names come from the boundaries table |
| umd_tree_cover_density_2000__threshold | Minimum canopy cover (%) in 2000 for a pixel to count as tree cover | 10, 15, 20, 25, 30, 50, 75 (plus 0, see below). GFW dashboards default to 30 |
| umd_tree_cover_loss__year | Year the loss was detected | 2001 onward. Detection can lag the event, especially late-year fires |
| is__umd_regional_primary_forest_2001 | Inside humid tropical primary forest (2001 map) | Only the humid tropics: in India, mostly the Northeast, Western Ghats and Andaman & Nicobar |
| wri_google_tree_cover_loss_drivers__driver | Dominant driver of loss in the surrounding 1 km cell | One driver per 1 km cell, not per pixel |
| wdpa_protected_areas__iucn_cat | IUCN category if inside a protected area, else empty | |
| gfw_planted_forests__type | Plantation type if inside a mapped plantation, else empty | |
| umd_tree_cover_loss__ha | Hectares of tree cover lost | The main measure |
| umd_tree_cover_loss_from_fires__ha | Hectares of that loss caused by fire | Subset of the loss |
| gfw_gross_emissions_co2e_all_gases__Mg | Gross greenhouse gas emissions from the loss | Mg = tonnes CO2e |
| area__ha | Land area of the row's slice of the district | Summary table only |
| umd_tree_cover_extent_2000__ha | Tree cover in 2000 at the row's threshold | Denominator for loss rates |
| alert__year, alert__week, alert__count | VIIRS fire alerts per ISO week | confidence__cat is h / n / l |

## First answers
Queried 2026-10-25 against the pinned versions, iso = 'IND'.

**Rows in tcl_change:** 1,477,495 (all thresholds).

**Loss (ha) by threshold, tcl_change.** Never sum across thresholds: each hectare is listed once per threshold it clears.

| Threshold | Loss ha |
|---|---|
| 0 | 3,268,363 |
| 10 | 2,619,067 |
| 15 | 2,552,399 |
| 20 | 2,521,052 |
| 25 | 2,486,317 |
| 30 | 2,425,650 |
| 50 | 2,138,665 |
| 75 | 1,263,437 |

The table also has a threshold 0 that the guide does not list. Check what it means before the grain check in Phase 7.

**Driver labels (row counts), tcl_change.** These become a lookup table in Phase 12.

| Driver | Rows |
|---|---|
| Permanent agriculture | 437,978 |
| Unknown | 269,660 |
| Logging | 214,177 |
| Shifting cultivation | 182,511 |
| Settlements & Infrastructure | 150,029 |
| Other natural disturbances | 134,942 |
| Hard commodities | 60,461 |
| Wildfire | 27,737 |

**Fire alerts by threshold, viirs_weekly.** Needed to decide `viirs_threshold`.

| Threshold | Alerts |
|---|---|
| 0 | 4,298,213 |
| 10 | 676,839 |
| 15 | 534,779 |
| 20 | 365,071 |
| 25 | 306,095 |
| 30 | 960,406 |
| 50 | 1,000,280 |
| 75 | 463,193 |

Alerts do not shrink as the threshold rises (30 and 50 are higher than 25), so unlike loss these rows may not be nested. Look at this before choosing a threshold.

## First look
From `docs/profiles/` and `notebooks/01_first_look.ipynb`, India only. Row counts below are `tcl_change` (545,568 rows, thresholds 10 to 75).

**Columns that are always empty.** None. Two are mostly empty on purpose, because empty means "not in one":
- `iucn_cat` is empty in 95.2% of rows. Only 4.8% of rows sit in a protected area, so `is_protected` is a thin slice. Check it still has enough rows before slicing by district and year.
- `plantation_type` is empty in 70.8% of rows. 29.2% of rows have a type, so a plantation slicer is viable. But 13% of rows are labelled `Unknown`, which is a type that exists in the data, not an empty value.

**Share of rows with a driver.** 100%. There are no empty values. Loss with no mapped driver arrives as the label `Unknown` (21.1% of rows), so the model needs no separate bucket. It is a real category, not missing data.

**Districts.**

| | Count |
|---|---|
| States with any loss | 34 |
| Districts with any loss | 626 |
| States in GADM 4.1 | 35 |
| Districts in GADM 4.1 | 634 |

The 8 districts with no loss rows are Sheikhpura, Diu, Botad, Lakshadweep, Mumbai City, Bikaner, Churu and Jaisalmer: small islands, a city, or desert. Lakshadweep is the one missing state. GADM 4.1 predates recent district splits, so "district" here means the GADM 4.1 district, about 634, not today's roughly 750. Some names repeat inside different states (Raigarh, Aurangabad, Bilaspur), so always join on `adm1` + `adm2`, never on the name.

**Zeros, negatives, maxima.**
- No negative values in `loss_ha`, `fire_loss_ha` or `emissions_t`.
- `loss_ha` is exactly 0 in 4.5% of rows, `fire_loss_ha` in 64.8%. Zero-loss rows carry no information, but they are kept for now.
- The largest single row is 8,606 ha: Lunglei district, Mizoram (`adm1` 23, `adm2` 5), threshold 10, year 2017, driver Shifting cultivation. Plausible for shifting cultivation, but look it up on the GFW map before trusting it in a headline.
- The median row loses about 1 ha, so the distribution is heavily skewed. Use sums, not averages, in the report.

**Precision.** Areas are floats such as `0.0759550059049479`. They come from 30 m pixels, so the smallest non-zero value is about 0.065 ha, roughly one pixel. Round to whole hectares in anything presented.

**Other notes.**
- The pulled `tcl_change` has 7 thresholds (10 to 75). The threshold 0 seen in "First answers" is not in this pull.
- `is_primary` is True in 23% of rows.
- All 24,637 rows with `loss_ha` = 0 have non-zero `emissions_t`. Find out why before relying on the two columns together.
