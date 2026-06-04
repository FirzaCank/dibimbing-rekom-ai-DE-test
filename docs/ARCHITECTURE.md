# Task 2: Data Architecture

Pipeline to ingest country data from the REST Countries API into a modern data stack
with three layers: Staging (raw), ODS (cleaned + deduplicated), and DWH (dimensional
model for analytics). This document is the written companion to the diagram; the diagram
screenshot goes in the submission document.

## Flow

```
REST Countries API
      |
      v
[ Ingestion: Custom Python ETL ]   (the Task 1 service, scheduled)
      |
      v
[ Staging Layer: GCS ]             raw JSON as-is, immutable, partitioned by ingest date
      |
      v  (dbt / ELT load)
[ ODS: PostgreSQL ]                cleaned, typed, deduplicated on cca3 + lang_code
      |
      v  (dbt models)
[ DWH: BigQuery ]                  star schema for analytics
      |
      v
[ BI / Analytics ]                 Looker Studio / Metabase
```

## Star schema (DWH)

```
                 dim_country
                 -----------
                 country_key (PK)
                 cca3
                 country_name
                 region
                 subregion
                      ^
                      |
fact_country_language |          dim_language
----------------------+          ------------
country_language_key (PK)  <----  language_key (PK)
country_key (FK) ----------+      lang_code
language_key (FK) ----------      lang_name
ingest_date (FK to dim_date)
```

- Grain: one row per (country, language) pair, matching the Task 1 normalized row.
- `fact_country_language` is a factless fact (it records the existence of a relationship);
  this is the correct pattern when the "measure" is the association itself.
- Conformed dimensions: `dim_country`, `dim_language`, `dim_date`.

## Tool choices and justification

| Layer | Tool | Why (performance / cost / ops) |
|---|---|---|
| Source | REST Countries API | Given by the task. Free, no API key, REST/JSON. |
| Ingestion | Custom Python ETL (reuse Task 1) | Already built and tested in Task 1. One simple, low-volume source does not justify standing up and maintaining Airbyte (extra infra + cost). Reusing the service means one codebase, not two. If sources later grew to dozens of SaaS APIs, Airbyte's connector catalog would then justify the switch. |
| Staging | GCS (Google Cloud Storage) | Cheapest durable landing zone for raw JSON; object storage is far cheaper per GB than a database. Immutable, append-only by ingest date, so any downstream layer can be fully rebuilt (replayable). Decouples ingestion from transformation. |
| ODS | PostgreSQL | Cleaning, typing, and deduplication are row-level operational work that a relational engine handles well (constraints, upserts, unique keys on cca3 + lang_code). Same engine as Task 1, so no new operational skill set. Low cost at this data size. |
| DWH | BigQuery | Serverless: no cluster to size or manage, pay-per-query and pay-per-storage. Columnar + massively parallel, so star-schema analytical scans are fast without index tuning. Scales from this tiny dataset to large ones with no re-architecture. Fits the stated GCP environment. |
| Transform | dbt | SQL-native (the team already writes SQL), version-controlled models, built-in tests and lineage/docs, CI/CD friendly. Models the Staging -> ODS -> DWH transformations as code with `ref()` dependency management. Cheaper and simpler than standing up Spark for a dataset this size; Spark would only pay off at much larger scale or for non-SQL transforms. |
| Orchestration (optional) | Airflow / Cloud Composer or cron | Schedule the daily ingest + dbt run. For a single daily pipeline, cron is enough; Airflow is the choice once there are dependencies across many pipelines. |

## Why this layering

- **Staging (GCS):** keep raw exactly as received so transformations are reproducible and
  the source API does not need to be re-hit to rebuild downstream data.
- **ODS (PostgreSQL):** this is where the deduplication called out in Task 1's known
  behavior (append-only inserts can duplicate rows) is resolved, using a unique key on
  (cca3, lang_code). Operational, current-state view.
- **DWH (BigQuery):** dimensional model optimized for analytical reads, decoupled from the
  operational store so heavy queries do not affect operational workloads.

## Cost / scale note

Everything above is sized for a small, slowly-changing dataset (a few hundred country-language
rows). The deliberate choices are: object storage for cheap raw retention, a serverless DWH so
there is no idle cluster cost, and dbt instead of Spark to avoid cluster overhead. Nothing here
is provisioned beyond what the volume needs, and each component has a clear upgrade trigger
(Airbyte at many sources, Spark at large volume, Airflow at many pipelines).
