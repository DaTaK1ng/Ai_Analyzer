# PRD: AI Multi-Source Analytics Demo

*Reverse-engineered from the current app. Short reference for what the product does and what it needs.*

---

## What it is

A demo app: you type something like “sales by category” and get a chart. Under the hood it runs **CSV → ETL → DuckDB**, then **your sentence → AI (or keyword fallback) → SQL → chart**. It supports **multiple data sources** (e.g. Sales, Events); you pick one, run ETL if needed, then use the same “type and get a chart” flow. Everything is local (Ollama optional); no API keys.

**Main idea:** One sentence in, one chart out — and you can switch datasets without changing the flow.

---

## Who it’s for

- **Presenters** — Show a full pipeline in a few minutes, no cloud setup.
- **Learners** — Try different phrasings and see how the app picks dimensions, metrics, and chart type; inspect the generated SQL.

---

## Core concepts

- **Data source** — One CSV + config (which columns are dimensions/metrics, date column, target DuckDB). Each source has its own DB and its own “last chart” state.
- **ETL** — Read CSV, clean (dates, numbers, trim strings), load into DuckDB. Run per source from the UI or CLI.
- **Plan** — The app turns your sentence into: dimension (what to group by), metric (what to sum), chart type (bar/line/pie), and optionally “by time with breakdown.” That’s the plan. It comes from Ollama when available, or from simple keyword rules (fallback).
- **Dimension / metric** — Dimension = group-by column (e.g. category, region, date). Metric = numeric column we aggregate (e.g. sales, revenue).

---

## What the product must do

**Data sources**

- Support multiple sources in one config; each has name, CSV path, DuckDB path, table, date column, breakdown dimension, columns, dimensions, metrics, and labels.
- UI: a source selector; the rest of the screen (DB overview, hints, ETL button, chart) follows the selected source. Chart state is per source so switching doesn’t mix things up.

**ETL**

- Run per source: read CSV, clean, write to that source’s DuckDB. Can be triggered from the dashboard or from the command line with an optional source id. Uses the config for column list, date column, and which columns are numeric vs string; drops rows with null date.

**From sentence to chart**

- Take free text → produce a plan (dimension, metric, chart type, optional by_time_breakdown). Prefer Ollama with a short prompt; if it’s down or times out, use keyword fallback so the user still gets a chart. Optionally cache plans for the same (source + input) to avoid repeated LLM calls.
- Generate and run SQL from the plan (group by dimension, sum metric; for “date” we aggregate by month; for breakdown-over-time we add the breakdown dimension). Show the SQL and the result table.
- Draw bar/line/pie from the result; support time series and categorical; for line-with-breakdown, one line per breakdown. Show a short summary (e.g. total, top 3, or time range).

**Dashboard**

- Show the pipeline (CSV → ETL → DuckDB → your words → AI → SQL → chart) and hints like “you can ask for X by Y; bar, line, pie.” Expandable schema + data preview for the current source. Clear messages when ETL hasn’t been run, DB is missing, or Ollama isn’t available.

---

## Non‑functional expectations

- ETL for a few thousand rows should finish in seconds. If we call the LLM, use a short timeout (e.g. 12 s) and fall back on failure so the user always gets a chart. Repeating the same request can use a cached plan.
- UI in English, single linear flow: pick source → run ETL if needed → type request → generate chart. No wizard.
- Runs locally (Python, Streamlit, DuckDB). Ollama is optional; without it we rely on keyword fallback. Adding a new source = add one config block + put CSV in place + run ETL — no code change in ETL or dashboard.
- No API keys for the default path; data stays on the machine (CSV + DuckDB).

---

## Assumptions and stack

- Input: tabular CSV with headers. Each source has one date column and at least one numeric column; dimensions/metrics are listed in config.
- Tech: Python, Streamlit, DuckDB, optional Ollama; charts with Plotly (bar, line, pie). Sources live in one config structure (e.g. `config/sources.py`).

---

## Out of scope (for now)

Auto-inferring ETL config from a random CSV, uploading CSV from the UI, editing/deleting sources in the UI, custom chart types, auth, or production hardening.

---

## Where it lives in code

| What | Where |
|------|--------|
| Source config | `config/sources.py` |
| ETL | `ETL/run_etl.py` |
| NL → plan | `Ai/llm.py`, `Ai/prompt.py`, Dashboard fallback |
| Query | Dashboard `_run_query`, `Ai/query.py` |
| Charts | `Dashboard/charts.py` |
| Summary | `Ai/report.py` |
| UI | `Dashboard/app.py` |
