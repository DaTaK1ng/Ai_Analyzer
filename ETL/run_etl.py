"""
ETL: read CSV for a data source, clean, write to DuckDB.
Run from project root: python ETL/run_etl.py [source_id]
Default source_id is "sales". Use "events" for events.csv.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pandas as pd
import duckdb

from config.sources import SOURCES, resolve_source_paths


def run(source_id: str = "sales"):
    cfg = resolve_source_paths(source_id)
    csv_path = cfg["csv_path"]
    db_path = cfg["db_path"]
    table = cfg["table"]
    columns = cfg["columns"]
    date_column = cfg["date_column"]
    metrics = cfg["metrics"]

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing data: {csv_path}")

    df = pd.read_csv(csv_path, encoding="utf-8")
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    for c in columns:
        if c not in df.columns:
            raise ValueError(f"CSV missing column: {c}. Columns: {list(df.columns)}")
    df = df[columns].copy()

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    for col in metrics:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[date_column])
    for col in columns:
        if col != date_column and col not in metrics:
            df[col] = df[col].astype(str).str.strip()

    conn = duckdb.connect(db_path)
    conn.execute(f"DROP TABLE IF EXISTS {table}")
    conn.register("df", df)
    conn.execute(f"CREATE TABLE {table} AS SELECT * FROM df")
    conn.close()
    print(f"ETL done ({source_id}): {len(df)} rows -> {db_path} [{table}]")


if __name__ == "__main__":
    source_id = sys.argv[1] if len(sys.argv) > 1 else "sales"
    if source_id not in SOURCES:
        print(f"Unknown source: {source_id}. Available: {list(SOURCES.keys())}")
        sys.exit(1)
    run(source_id)
