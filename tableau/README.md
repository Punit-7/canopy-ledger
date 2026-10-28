# Tableau Public dashboard: build steps

A one-screen dashboard ("how much, where, why") plus a Fire dashboard and a Two-definitions dashboard, published at a public link.
Built from CSV exports of the same marts as the Power BI report, so every number can be reconciled across the two tools.
Allow about half a day.

**Files in this folder**

| File | Use |
|---|---|
| `calculated_fields.md` | Every calculated field, to paste in step 5. |
| `README.md` | These steps. |

Tableau Public reads files, not databases. Everything you publish is public, so only use public data (this project does).

---

## 0. What must exist first

- [ ] The marts are built (`dbt build` passes) and the database is running on **port 5435**.
- [ ] **The export step is not built in this repo yet.** The guide describes it in Phase 17.2: `src/ledger/export.py`, a `ledger export` command and five SQL files in `sql/export/`. Do that first, or Tableau has nothing to read. When it exists, you run:

```powershell
dotenv -f .env run -- ledger export --out exports/tableau
```

and get five files (`exports/` is git-ignored):

| File | One row is | Relates to |
|---|---|---|
| `tableau_loss.csv` | Loss for one district, year, driver and forest-type combination (30% canopy) | districts, on `district_id` |
| `tableau_districts.csv` | One district with its land area and 2000/2010 tree cover | the centre |
| `tableau_fire.csv` | Fire alerts for one district, month and confidence level | districts, on `district_id` |
| `tableau_state_compare.csv` | One state, GFW vs ISFR | a separate data source |
| `tableau_meta.csv` | One loaded source with its GFW version | a separate data source |

**Never export one wide file** with each district's tree cover copied onto every loss row. `SUM(tree cover)` would then add the same district hundreds of times. Stocks stay in the districts file, and Tableau's relationships aggregate each table at its own grain.

## 1. Install and sign in

1. Create a free profile at public.tableau.com.
2. Install **Tableau Desktop Public Edition** from the same site and sign in.

## 2. Connect and relate

1. Connect > To a file > Text file > `tableau_loss.csv`.
2. Drag `tableau_districts.csv` onto the canvas. Set the relationship to **District Id = District Id**.
3. Drag `tableau_fire.csv` onto the canvas and relate it to **districts**, not to loss, on District Id.
4. Data > New Data Source for `tableau_state_compare.csv`, and again for `tableau_meta.csv`. Keep these separate.

## 3. Tidy the fields

- [ ] Rename `Year` in the loss table to **Loss Year** and `Year` in the fire table to **Alert Year**. Two fields called "Year" is a mistake waiting to happen.
- [ ] Convert Loss Year and Alert Year to discrete dimensions (right-click > Convert to Discrete). Set Month Start to a Date.
- [ ] Check that Is Deforestation, Is Primary Forest, Is Protected and Is Plantation are Boolean.
- [ ] Hide District Id in every table, `Rows`, `Loaded At` and anything no sheet needs.
- [ ] Create a hierarchy: drag **State District** onto **State**, name it Geography. Use State District in sheets, not District: district names repeat across states.
- [ ] Default number format for hectare fields: Number (Custom), 0 decimals, thousands separator.

## 4. Check the data before building

Drop `SUM(Loss Ha)` on a text sheet with no filters.

| Check | Expected |
|---|---|
| `SUM(Loss Ha)` | 2,425,650 |
| `SUM(Loss Ha)` with Loss Year ≤ 2024 | 2,307,054 |
| Number of State District values | 634 in districts; 602 have loss |

If the total is a multiple of this, a relationship is repeating rows. Re-check step 2.

## 5. Calculated fields

Create every field in `calculated_fields.md`, in the order given. Two are traps:

- `Last Year` uses `{ FIXED : ... }`, so the KPI cards always show the newest year regardless of the year filter.
- The Pareto needs a **table-calculation filter** (`[Top 50 districts]` = True), not an ordinary Top N filter. An ordinary filter makes the curve hit 100% at district 50.

## 6. Worksheets

Build one sheet per row. Name each sheet by what it shows: the names appear in tooltips and in the layout tree.

| Sheet | Build |
|---|---|
| KPIs | Measure Names on Columns, Measure Values on Text. Keep Loss (ha), Loss last year (ha), Loss YoY % last year, Deforestation share %, Emissions (Mt CO2e). Format as big numbers with small labels. |
| Trend | Loss Year on Columns, Loss (ha) on Rows as bars, Loss 3-yr avg on a second Rows axis as a line. Dual Axis, Synchronize Axis. Add a shaded reference band for 2001–2014 labelled "earlier methods". |
| Era note | `Method era note` on Text. Empty when the selection stays within one era. |
| States | State on Rows, Loss (ha) on Columns, sorted descending, top 15 with a rank filter. |
| Districts | State District on Rows. District rank, Loss (ha), Loss rate %, Share of national % on Text. Rank filter at 25. |
| Pareto | State District on Columns sorted by Loss (ha) descending, Cumulative share % on Rows as a line. Reference lines at 50% and 80%. Filter `[Top 50 districts]` (or 100). |
| Drivers | Loss Year on Columns, Loss (ha) on Rows, Driver on Color, stacked bars. |
| Fire heatmap | Alert Year on Columns, MONTH(Month Start) on Rows, Square marks, High-confidence alerts on Color (sequential orange). |
| Fire vs loss | State District on Detail, High-confidence alerts on Columns, SUM(Fire Loss Ha) on Rows, both axes logarithmic. Filter Loss Year ≥ 2012, when the alert data starts. |
| Two definitions | From `tableau_state_compare`: State on Rows, GFW tree cover 2000 km² and ISFR forest cover 2023 km² side by side. |
| Version | `Data version` on Text, small grey type, for the footer. |

**Driver colours** (the same as Power BI so the two read as one project):

| Driver | Colour |
|---|---|
| Permanent agriculture | `#b07a3c` |
| Hard commodities | `#9a5b4c` |
| Settlements and infrastructure | `#5a4e6e` |
| Shifting cultivation | `#c9a35b` |
| Logging | `#7d9c8a` |
| Wildfire | `#c0392b` |
| Other natural disturbances | `#8a8f86` |
| Unknown | `#c8ccc6` |

## 7. Dashboards

**Dashboard 1, "Tree cover loss in India"** (Size: Fixed, 1200 × 1100):

```
┌──────────────────────────────────────────────────────────────────────┐
│ Title · one-line subtitle stating the question                       │
│ KPIs: total · last year (YoY) · deforestation share · emissions      │
├──────────────────────────────────────┬───────────────────────────────┤
│ Trend (bars + 3-yr average)          │ States (top 15)               │
│ Era note                             │                               │
├──────────────────────────────────────┼───────────────────────────────┤
│ Drivers by year                      │ Districts (top 25)            │
├──────────────────────────────────────┴───────────────────────────────┤
│ Loss Year filter (range) · About the data · Version                  │
└──────────────────────────────────────────────────────────────────────┘
```

**Dashboard 2, "Fire":** heatmap on top, scatter below, a short text box saying what VIIRS alerts measure (active fires of any kind, including crop burning, so alerts are a weak guide to fire loss).

**Dashboard 3, "Two definitions":** the comparison sheet plus a text box: ISFR measures net forest stock including plantations; GFW measures gross canopy removal.

**Interactions** (what makes it a dashboard rather than a page of charts):

1. Dashboard > Actions > Add Action > Filter: source States, targets Districts and Trend, run on Select, clearing shows all values.
2. Highlight action on Driver, so hovering a driver in Drivers highlights it everywhere.
3. Apply the Loss Year filter to Trend, Drivers, States and Districts, **not** to KPIs: the KPI cards always describe the newest year.
4. Navigation buttons (Objects > Navigation) between the three dashboards.
5. Device layout: Dashboard > Device Preview > Add Phone Layout. Stack KPIs, Trend and Districts.
6. Write the tooltips yourself (Marks > Tooltip), one sentence each, for example: "Mizoram lost 274,262 ha in 2015–2025, 14% of its 2000 tree cover."

## 8. Reconcile with SQL and Power BI

Before publishing, all three tools should agree to the hectare.

| Check | SQL | Power BI | Tableau | Expected |
|---|---|---|---|---|
| Total loss, all years | `select sum(loss_ha) from marts.fct_tree_cover_loss` | Loss (ha) card | KPIs sheet | 2,425,650 |
| Loss in 2020 | `01_national_trend.sql` | Trend table | Trend tooltip | 130,855 |
| Rank 1 district since 2015 | `02_top_districts.sql` | Districts table | Districts sheet | Karbi Anglong, 79,541 |
| Districts for 50% of loss, 2015+ | `03_pareto.sql` (add `where year >= 2015`) | Pareto chart | Pareto sheet at 50% | 17 |

The only expected difference is the moving average: SQL centres it, while Power BI and Tableau use a trailing average.
If Tableau's loss rate looks too small, a stock column is being summed across too many rows. Re-check the relationships.

## 9. Publish

1. File > Save to Tableau Public As > **Canopy Ledger: India tree cover loss**. Tableau extracts the CSVs into the workbook and uploads it.
2. On the published page, open Settings: turn off "Show sheets as tabs" (the navigation buttons replace them), add a description with one sentence on the question and the GitHub link, set the thumbnail to Dashboard 1.
3. Copy the public link into the repo README. Take a screenshot of Dashboard 1 for it.

## 10. Refresh when GFW publishes new data

1. Re-run `dbt build`, then `ledger export` to regenerate the CSVs.
2. In Tableau: Data > Refresh on each data source, and check that the Version sheet shows the new GFW version.
3. File > Save to Tableau Public with the same name, so the link stays the same.

GFW publishes loss data about once a year, so this is a yearly task plus any corrections.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| Loss totals are hundreds of times too large | A wide export or a wrong relationship is repeating rows. Check step 2. |
| Pareto reaches 100% at district 50 | Ordinary Top N filter. Use the table-calculation filter (step 5). |
| KPIs change when the year filter moves | The Loss Year filter is applied to the KPI sheet. Remove it from KPIs. |
| A district shows up twice | You used District instead of State District. |
| Fire and loss axes look empty on the scatter | Zero values on a log axis. Filter to Loss Year ≥ 2012 and exclude zeros. |
