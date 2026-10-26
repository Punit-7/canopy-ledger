# docs/decisions.md

## 2026-10-25 · GFW version
Pinned gadm__tcl__adm2_change and _summary to v20260424: max(year) = 2025.
The "latest" tag for tcl_change still points to v20250515 (max year 2024). Both tables use the same version so loss and extent come from the same run.

## 2026-10-26 · Canopy threshold
Headline loss uses a 30% canopy threshold (`canopy_threshold = 30` in `configs/sources.toml`). It matches the GFW dashboard default, so our totals can be checked against a published number.
Every threshold (10 to 75) stays in the raw table, because each hectare is listed once per threshold it clears. Summing across thresholds double counts, so every analysis filters to one threshold first (`explore.at_threshold`).
Threshold sensitivity: loss at 10% is 108% of loss at 30%; at 75% it is 52%.

## 2026-10-26 · Fire-alert threshold and confidence
VIIRS alerts use threshold 30 and high confidence only. Using 30 keeps the alerts on the same definition of "tree" as the loss. High confidence drops noisy low and nominal alerts.
Alert rows are not nested across thresholds (30 and 50 have more alerts than 25), so alerts must never be summed across thresholds. The VIIRS table pinned is v20251202 and starts in 2012, so fire comparisons start in 2012.

## 2026-10-26 · Unmatched names
Every `adm1`/`adm2` code in the loss table has a name in GADM 4.1 (the `names.every_district_named` check finds 0 orphans), so nothing was dropped or renamed.
8 of the 634 GADM districts have no loss rows (Sheikhpura, Diu, Botad, Lakshadweep, Mumbai City, Bikaner, Churu, Jaisalmer); they stay in the name table.
District names repeat across states (for example Raigarh, Aurangabad, Bilaspur), so joins use `adm1` + `adm2`, never the name.

## 2026-10-26 · Reference check year
`ledger checks --reference-ha 2310000` is GFW's 2001–2024 figure, but the pinned data runs to 2025, so it fails by about 5% (the extra year). The reconciliation was done by hand on 2001–2024: 2,307,054 ha vs 2,310,000 ha (0.13% apart). Update the reference when GFW's dashboard shows 2025.

## ISFR state mapping (open)
Not decided yet. `warehouse/seeds/isfr_2023_states.csv` has not been created, so there is no state mapping to record. Add the entry (including how names like "Delhi" vs "NCT of Delhi" are matched) when it is.
