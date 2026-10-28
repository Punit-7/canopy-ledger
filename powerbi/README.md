# Power BI report: build steps

A six-page report on the warehouse marts, saved as a Power BI project (`.pbip`, text files) so git shows what changed.
Allow about half a day. Windows only (Power BI Desktop).

**Files in this folder**

| File | Use |
|---|---|
| `theme.json` | Colours and fonts. Apply in step 6. |
| `measures.dax` | Every measure, with its display folder. Copy from it in step 5. |
| `canopy-ledger.pbip` + folders | Created by you in step 2 and committed. |

---

## 0. Before you start

- [ ] Docker Desktop is running and the database container is healthy: `docker compose ps`.
- [ ] The marts exist: `dotenv -f .env run -- dbt build --project-dir warehouse --profiles-dir warehouse` finishes with 0 errors.
- [ ] Install Power BI Desktop from the Microsoft Store (free).
- [ ] **Use port 5435, not 5432.** A native PostgreSQL 18 service on this machine owns 5432. It rejects the `ledger` login, so connecting there gives "password authentication failed".
- [ ] The *Two definitions* page needs `warehouse/seeds/isfr_2023_states.csv` filled in (it is header-only now), followed by `dbt seed` and `dbt run -s mart_state_gfw_vs_isfr`. Until then, the ISFR columns are empty.

## 1. Enable and save as a project

1. File > Options and settings > Options > Preview features: tick **Power BI Project (.pbip) save option**. Restart Power BI Desktop.
2. Open a blank report. Before adding data: File > Save as > type **Power BI project files (*.pbip)**.
3. Save as `canopy-ledger.pbip` in this folder (`powerbi/`).

## 2. Connect to PostgreSQL

1. Home > Get data > **PostgreSQL database**.
2. Server `localhost:5435`, Database `ledger`, mode **Import** (not DirectQuery: the data changes about once a year and is small).
3. Credentials > Database: user `ledger`, password from your `.env`.
4. If asked about encryption, accept the unencrypted connection: the local Docker database has no SSL.
5. In the Navigator, tick only these seven tables from the `marts` schema:
   `dim_district`, `dim_year`, `dim_driver`, `fct_tree_cover_loss`, `fct_fire_alerts`, `mart_state_gfw_vs_isfr`, `meta_data_versions`.
6. Click **Transform data**. Rename each query to drop the prefix, for example `marts fct_tree_cover_loss` to `fct_tree_cover_loss`. The measures refer to the short names.
7. Create two parameters (Home > Manage parameters): `PgServer` = `localhost:5435` and `PgDatabase` = `ledger`. In each query's Source step, replace the two strings with the parameters. To point at Neon later you change two values, not seven queries.
8. Close & Apply.

**Check:** the row counts after load should be `dim_district` 634, `dim_year` 25, `dim_driver` 8, `fct_tree_cover_loss` 77,026, `fct_fire_alerts` 108,482.

## 3. Relationships (Model view)

Delete everything Power BI auto-detected, then create these. All are many-to-one, single direction.

| From (many) | To (one) |
|---|---|
| `fct_tree_cover_loss[district_id]` | `dim_district[district_id]` |
| `fct_tree_cover_loss[year]` | `dim_year[year]` |
| `fct_tree_cover_loss[driver_id]` | `dim_driver[driver_id]` |
| `fct_fire_alerts[district_id]` | `dim_district[district_id]` |
| `fct_fire_alerts[year]` | `dim_year[year]` |

`mart_state_gfw_vs_isfr` and `meta_data_versions` stay unconnected.

## 4. Tidy the model

- [ ] Hide every key column (`district_id`, `driver_id`, `adm1`, `adm2`) and every raw measure column in the facts. Report builders must use measures, not drag `loss_ha` onto a visual and get an implicit sum.
- [ ] Sort `dim_driver[driver]` by `sort_order` (Column tools > Sort by column).
- [ ] Hierarchy on `dim_district`: `state` > `state_district`. Use `state_district` in visuals, not `district`: district names repeat across states (Raigarh, Aurangabad, Bilaspur).
- [ ] Data category: `dim_district[state]` as State or Province.
- [ ] Formats: hectares as whole numbers with a thousands separator; percentages with one decimal.
- [ ] Home > Enter data: create a table named `_Measures`. Delete its one column once the first measure is in it.

## 5. Measures

Open `measures.dax`. For each measure: select `_Measures`, Home > New measure, paste it, then set its display folder (Properties pane). The folders are Loss, Rates, Time, Ranking, Fire and About.

**Measures to build (22):**
Loss (ha), Loss (kha), Primary forest loss (ha), Deforestation (ha), Deforestation share %, Fire loss (ha), Fire share %, Emissions (Mt CO2e), Tree cover 2000 (ha), Loss rate %, Share of national loss %, Loss 3-yr avg (ha), Loss previous year (ha), Loss YoY %, Loss last year (ha), Loss YoY % last year, Method era warning, District rank, Cumulative share %, Fire alerts, High-confidence alerts, Data version.

### 5.1 Test the measures against SQL (do not skip)

1. Add a new page called `scratch`. Put a **table** visual on it with `dim_year[year]`, `Loss (ha)`, `Loss 3-yr avg (ha)`, `Loss YoY %`.
2. Compare with `sql/analysis/01_national_trend.sql`. `Loss (ha)` and YoY must match exactly. The moving average differs on purpose: SQL centres it, DAX trails it.
3. Add a second table: `state_district`, `Loss (ha)`, `District rank`. Set a year filter of 2015–2025 and compare with `02_top_districts.sql`.
4. Delete the scratch page when they match.

**Numbers that must come out:**

| Check | Expected |
|---|---|
| Loss (ha), all years | 2,425,650 |
| Loss (ha), 2001–2024 | 2,307,054 (GFW dashboard: 2.31 Mha) |
| Loss, 2025 | 118,595 (provisional) |
| Deforestation share % | 39.5% |
| Emissions, all years | about 1,365 Mt CO2e (1.36 Gt) |
| Rank 1 district since 2015 | Karbi Anglong, Assam: 79,541 ha |

If a total is far too large, a measure is summing across canopy thresholds. That cannot happen here (the marts hold only 30%), so look for a many-to-many or a missing relationship instead.

## 6. Theme

View > Themes > Browse for themes > `theme.json`.

Give each driver a fixed colour (Format pane > Colors, per driver) and reuse it on every page: agriculture and commodities warm, temporary classes muted, wildfire the strongest red.

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

## 7. Pages

Build in this order. Each page answers one question from `docs/eda_memo.md`.

### Page 1: Overview ("How much, and which way?")

1. **Slicer**, Between style: `dim_year[year]`, default 2015 to the last year.
2. **Cards** (six): `Loss (kha)` with the slicer interaction turned off (all years), `Loss last year (ha)`, `Loss YoY % last year`, `Primary forest loss (ha)`, `Deforestation share %`, `Emissions (Mt CO2e)`.
3. **Line and clustered column chart**: x = `dim_year[year]`, columns = `Loss (ha)`, line = `Loss 3-yr avg (ha)`.
4. **Card** under it: `Method era warning`.
5. Title every visual with unit and threshold, for example "Tree cover loss (ha, ≥30% canopy)".

Expect a step up around 2014–2017, peaking in 2017 (179,260 ha). That is partly a method change, not only clearing.

### Page 2: Where ("Which states and districts?")

1. **Slicer** on `dim_district[state]`.
2. **Bar chart**: y = `state`, x = `Loss (ha)`, sorted descending.
3. **Table**: `state_district`, `District rank`, `Loss (ha)`, `Loss rate %`, `Share of national loss %`. Turn on data bars for `Loss (ha)`.
4. **Pareto**: Line and clustered column chart, x = `state_district` sorted by `Loss (ha)` descending, columns = `Loss (ha)`, line = `Cumulative share %`. Visual filter: Top N = 50 by `Loss (ha)`.

Expect Mizoram first by hectares (19% of national loss), Tripura first by loss rate. With the slicer at 2015–2025, 17 districts make up half of all loss.

### Page 3: Why ("What is driving it?")

1. **Stacked column**: x = `year`, y = `Loss (ha)`, legend = `dim_driver[driver]`.
2. **100% stacked bar**: y = `state` (Top N 10 by loss), x = `Loss (ha)`, legend = `driver`.
3. Two simple bars: `Loss (ha)` by `is_primary_forest` and by `is_protected` (import these from the fact; they are the only fact columns you use directly as axes).

Expect shifting cultivation about 60% nationally and 73% in the Northeast.

### Page 4: Fire ("When do fires happen?")

1. **Matrix** (heatmap): rows = `fct_fire_alerts[month]`, columns = `year`, values = `High-confidence alerts`. Cell elements > Background colour > a sequential orange scale.
2. **Column chart**: x = `year`, y = `Fire loss (ha)`.
3. **Scatter**: details = `state_district`, x = `High-confidence alerts`, y = `Fire loss (ha)`. Set both axes to Log scale. Filter `year` ≥ 2012, the first year of VIIRS data.

Expect a spring peak (February to April) and a weak link between alerts and fire loss (correlation about 0.25).

### Page 5: Two definitions ("Why does the government report a gain?")

1. **Table** from `mart_state_gfw_vs_isfr`.
2. **Text box** summarising the comparison: ISFR counts net forest stock including plantations; GFW counts gross canopy loss. Both can be true.

### Page 6: About the data ("Can I trust this?")

Text box with the sources, the `Data version` card, the 30% canopy threshold, the caveats from `docs/eda_memo.md` (loss is not deforestation, method changes in 2011 and 2015, 2025 provisional, gross emissions only, GADM 4.1 districts) and the repo link.

### Drill-through: District detail

1. New page, drill-through field `dim_district[state_district]`.
2. Visuals: yearly trend, driver mix, fire alerts by month, `District rank`.

## 8. Production details

- [ ] Copy the `Data version` card into the footer of every page. A screenshot can then be traced to a data version.
- [ ] Add a tooltip page (Page information > Allow use as tooltip) with the district's rank, loss rate and top driver. Set it as the tooltip for the Where table and bar chart.
- [ ] Turn off interactions that make no sense (a year slicer should not filter the Two definitions table): Format > Edit interactions.
- [ ] View > Performance analyzer on each page. Any visual over one second points at a measure to simplify.
- [ ] Check View > Mobile layout for the Overview page.
- [ ] Add alt text to every visual (Format > General > Alt text): one sentence on what it shows.
- [ ] Optional map: only if it answers something the table does not. If you add one, use a simplified boundary file and say "GADM 4.1" on the page: GADM's external boundary does not match the Survey of India boundary.

## 9. Save and commit

```powershell
git add powerbi
git commit -m "Power BI report on marts"
```

Then File > Export > Export to PDF into `docs/`. That PDF is the file most reviewers will open.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| "password authentication failed for user ledger" | Connected to the native PostgreSQL on 5432. Use `localhost:5435`. |
| Can't connect at all | Docker Desktop is not running, or the container is stopped. `docker compose up -d`. |
| A district name appears twice in a table | You used `district`. Use `state_district`. |
| Totals ignore the year slicer on a card | Intended for `Loss last year` and the "all years" card: they remove the year filter. |
| `Cumulative share %` is slow | Keep the Top N filter at 50 to 100 on the Pareto visual. |
| Boolean filters show `TRUE`/`FALSE` as text | Set the column data type to True/False in Power Query. |
