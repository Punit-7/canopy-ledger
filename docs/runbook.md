# docs/runbook.md

What to do when the monthly refresh (`.github/workflows/refresh.yml`) fails, and how to adopt a new GFW release.

## What tells you something is wrong

| Signal | Where | Means |
|---|---|---|
| Failed refresh run | GitHub emails you (set Actions notifications to failed workflows only) | A pull, check, load or dbt test failed. The warehouse still has last month's data |
| `newer_versions_available` warning | Refresh job log | GFW published a version newer than the pinned one |
| Check lines with `"passed": false, "severity": "warn"` | Refresh job log | Suspicious but not blocking; read the detail |
| Footer "Data version" older than expected | The report | The refresh has not run or did not finish |

To make a newer version fail the job instead of warning, change the step to `ledger check-versions --strict` (exit code 3).

## A new GFW release is out (the yearly one usually arrives in spring)

1. `ledger versions`, then check `MAX(umd_tree_cover_loss__year)` on the new version.
2. On a branch: update the versions and `expect_max_loss_year` in `configs/sources.toml`, and `last_loss_year` in `warehouse/dbt_project.yml`.
3. `ledger extract && ledger profile && ledger checks` locally. `git diff docs/profiles/` shows what changed.
4. Re-run `notebooks/02_eda.ipynb`. Did any finding in `docs/eda_memo.md` change? Update the memo.
5. Check the dashboard reconciliation against the new GFW figure.
6. Open a pull request; merge when CI passes; run the refresh workflow by hand.

## When a step fails

| Failure | Cause and fix |
|---|---|
| `change.max_year` failed | The pinned version does not contain the expected year, or the download was cut short. Compare the manifest's `rows` with the previous run's |
| `names.every_district_named` failed | GFW moved the loss tables to a different GADM version. Find the matching boundaries version and pin it |
| dbt `relationships` test on `driver_id` failed | A new driver label appeared. Add it to `warehouse/seeds/driver_categories.csv` with its treatment, and note it in `docs/decisions.md` |
| `assert_fact_total_matches_staging` failed | A join is dropping or duplicating rows, almost always a driver label missing from the seed |
| GFW API returns 401 or 403 | The API key has expired (one year from creation). Create a new one and update the `GFW_API_KEY` secret in the `prod` environment |
| Neon "storage limit" error | Confirm `EXTRACT_THRESHOLDS: "30"` is set in the refresh workflow, then check sizes: `select relname, pg_size_pretty(pg_total_relation_size(oid)) from pg_class where relnamespace = 'raw'::regnamespace order by 2 desc;` |

## Secrets

Repo Settings > Environments > `prod`. Secrets: `GFW_API_KEY`, `DATABASE_URL`, `PGHOST`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`
(the `PG*` values are the same Neon connection split up for dbt; use the unpooled host).
