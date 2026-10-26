# Tree cover loss in India, 2001–2025: what the data shows

Data: GFW `gadm__tcl__adm2_change` v20260424 (UMD tree cover loss), 30% canopy threshold, GADM 4.1 districts.
Pulled 2026-10-25. Every number below is reproducible from `notebooks/02_eda.ipynb`.

## Findings

1. **Scale.** India lost 2.43 Mha of tree cover in 2001–2025 (2.31 Mha in 2001–2024, matching GFW's 2.31 Mha).
2. **Trend.** Average annual loss in 2021–2025 (124 kha) was 13% lower than in 2016–2020 (143 kha). Loss peaked in 2017 (179 kha).
   Comparisons with years before 2015 are affected by method changes: the 2001–2011 average was only 62 kha.
3. **Concentration.** 17 of the 415 districts with loss account for half of all loss since 2015. Sixteen are in the Northeast (Mizoram 5, Manipur 4, Assam 2, Meghalaya 2, Nagaland 2, Tripura 1); the other is Kandhamal, Odisha.
   The Northeast holds 74% of national loss. By loss rate (loss as a share of 2000 tree cover) Tripura (23.5%), Nagaland (21.0%) and Mizoram (18.2%) lead, not Assam, which is first by hectares.
4. **Drivers.** Shifting cultivation accounts for 60% of loss nationally and 73% in the Northeast; permanent agriculture is second (28%).
   Only about 40% falls in classes that count as deforestation (permanent agriculture, hard commodities, settlements, and shifting cultivation inside primary forest).
5. **Fire.** High-confidence VIIRS alerts peak in March, and February to April carries about 82% of them. Alert counts are a weak guide to fire-driven loss (Spearman r = 0.29 with fire loss, 0.23 with total loss, by district-year from 2012).
   Fire is also a small part of the loss: 1.6% of hectares.
6. **Definitions.** ISFR's rising forest cover (715,343 km², +156 km² since 2021) and GFW's continuous loss measure different things (net stock including plantations vs gross canopy removal) and do not contradict each other.
   A state-by-state comparison is not done yet (see "What I would do next").

## Other numbers worth knowing

- Primary forest holds 15% of loss; protected areas hold 0.4%.
- The canopy threshold matters little between 10% and 30% (loss at 10% is 8% higher) but a lot at 75% (loss is 48% lower).
- Gross emissions from the loss are 1.36 Gt CO₂e for 2001–2025 (1.29 Gt for 2001–2024, matching GFW's 1.29 Gt).

## Caveats (also shown on the report's About page)

- Tree cover loss is not deforestation; see finding 4.
- Method changes in 2011 and 2015; compare within eras.
- 2025 is provisional until the next GFW release.
- Gross emissions only; no regrowth.
- "District" means a GADM 4.1 district (634 of them), not today's roughly 750.
- Loss is rounded to the pixel: a 30 m pixel is about 0.09 ha, so quote hectares to the nearest thousand at national scale.

## What I would do next

- Type in the ISFR 2023 state table and compare by state (`warehouse/seeds/isfr_2023_states.csv`).
- Explain why every row with zero loss still has non-zero emissions (see `docs/data_dictionary.md`).
- Look up the largest single row (Lunglei, Mizoram, 2017, 8,606 ha) on the GFW map.
- Build `is_deforestation` in the warehouse from the driver and primary forest rule in finding 4.
