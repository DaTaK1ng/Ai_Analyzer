"""
Given dimension, metric, chart_type and source config: build SQL, run on DuckDB, return (DataFrame, SQL string).
"""
import duckdb
import pandas as pd


def get_db_stats(db_path: str, table: str, columns_str: str = "") -> dict:
    """Return dict with row_count, table, db_path, columns for sidebar."""
    try:
        conn = duckdb.connect(db_path)
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()
        return {"row_count": row_count, "table": table, "db_path": db_path, "columns": columns_str or "—"}
    except Exception:
        return {"row_count": 0, "table": table, "db_path": db_path, "columns": columns_str or "—"}


def get_schema(db_path: str, table: str) -> list:
    """Return list of (column_name, type) for the table."""
    try:
        conn = duckdb.connect(db_path)
        schema = conn.execute(f"DESCRIBE {table}").fetchall()
        conn.close()
        return schema
    except Exception:
        return []


def get_table_preview(db_path: str, table: str, limit: int = 200) -> pd.DataFrame:
    """Return DataFrame with first `limit` rows from table."""
    try:
        conn = duckdb.connect(db_path)
        df = conn.execute(f"SELECT * FROM {table} LIMIT {limit}").fetchdf()
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def run_query(
    dimension: str,
    metric: str,
    chart_type: str,
    db_path: str,
    table: str,
    dimensions_list: list,
    metrics_list: list,
    date_column: str,
    breakdown_dimension: str = None,
    breakdown_by_category: bool = False,
):
    """
    Return (df, sql_string).
    When breakdown_by_category=True and dimension is date, group by date and breakdown_dimension (one line per breakdown).
    dimensions_list: allowed dimension names (use "date" for time; we map to date_column in SQL).
    """
    if dimension not in dimensions_list:
        dimension = dimensions_list[0]
    if metric not in metrics_list:
        metric = metrics_list[0]

    # SQL column for grouping by "time": use actual date column
    group_col = date_column if dimension == "date" else dimension

    conn = duckdb.connect(db_path)
    if dimension == "date":
        if breakdown_by_category and breakdown_dimension:
            sql = f"""
            SELECT strftime({date_column}, '%Y-%m') AS date, {breakdown_dimension} AS category, SUM({metric}) AS value
            FROM {table}
            GROUP BY strftime({date_column}, '%Y-%m'), {breakdown_dimension}
            ORDER BY date, category
            """
        else:
            sql = f"""
            SELECT strftime({date_column}, '%Y-%m') AS date, SUM({metric}) AS value
            FROM {table}
            GROUP BY strftime({date_column}, '%Y-%m')
            ORDER BY date
            """
    else:
        sql = f"""
        SELECT {group_col} AS dim, SUM({metric}) AS value
        FROM {table}
        GROUP BY {group_col}
        ORDER BY value DESC
        """
    sql = sql.strip()
    df = conn.execute(sql).fetchdf()
    conn.close()
    return df, sql
