# Tableau calculated fields

Create each with Analysis > Create Calculated Field. Use the exact name in the comment above each formula.
Tableau turns `loss_ha` into `[Loss Ha]`, `fire_loss_ha` into `[Fire Loss Ha]`, and so on.
Tableau accepts `//` comments, so the formulas can be pasted as they are.

## Measures (loss table)

```
// Loss (ha)
SUM([Loss Ha])

// Loss rate %   (format as percentage, 2 decimals)
// Tree cover comes from the districts table, aggregated at its own grain by the relationship.
SUM([Loss Ha]) / SUM([Tree Cover 2000 Ha])

// Deforestation share %
SUM(IF [Is Deforestation] THEN [Loss Ha] END) / SUM([Loss Ha])

// Fire share %
SUM([Fire Loss Ha]) / SUM([Loss Ha])

// Emissions (Mt CO2e)
SUM([Emissions T Co2e]) / 1000000
```

## KPI fields (always describe the newest year)

```
// Last Year   (a FIXED expression ignores the view, so this is always the newest year in the data)
{ FIXED : MAX([Loss Year]) }

// Loss last year (ha)
SUM(IF [Loss Year] = [Last Year] THEN [Loss Ha] END)

// Loss previous year (ha)
SUM(IF [Loss Year] = [Last Year] - 1 THEN [Loss Ha] END)

// Loss YoY % last year
([Loss last year (ha)] - [Loss previous year (ha)]) / [Loss previous year (ha)]
```

## Table calculations

For each: right-click the field in the view > Edit Table Calculation, then set "Compute using" as noted.

```
// Loss 3-yr avg   (compute using: Loss Year)
// Trailing, like the Power BI measure: the 2025 value averages 2023–2025.
WINDOW_AVG(SUM([Loss Ha]), -2, 0)

// Loss YoY %   (compute using: Loss Year)
(SUM([Loss Ha]) - LOOKUP(SUM([Loss Ha]), -1)) / LOOKUP(SUM([Loss Ha]), -1)

// District rank   (compute using: State District)
RANK_DENSE(SUM([Loss Ha]))

// Share of national %   (compute using: State District)
SUM([Loss Ha]) / TOTAL(SUM([Loss Ha]))

// Cumulative share %   (compute using: State District, sorted by Loss (ha) descending)
RUNNING_SUM(SUM([Loss Ha])) / TOTAL(SUM([Loss Ha]))

// Method era note
IF COUNTD([Method Era]) > 1
THEN "The selected years cross a change in the UMD method (2011, 2015). Compare years within one era."
END

// Top 50 districts   (for the Pareto sheet; use as a filter, keep True)
[District rank] <= 50
```

### Filter order matters

Tableau applies dimension filters before table calculations. If you keep the top 50 districts with an ordinary filter, `TOTAL()` only sees those 50, and the Pareto curve reaches 100% at district 50.
To show the top 50 while keeping the national total, filter on the table calculation: put `[Top 50 districts]` on Filters and keep **True**. Table-calculation filters run last, after `TOTAL()` is computed.

## Fire table

```
// High-confidence alerts   (fire table)
SUM(IF [Confidence] = "h" THEN [Alerts] END)
```

## Meta data source (put on a text-only sheet)

```
// Data version
"GFW " + MAX(IF [Source] = "tcl_change" THEN [Version] END)
+ " · 30% canopy · GADM 4.1 districts"
```
