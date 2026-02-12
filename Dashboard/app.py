"""
Streamlit app: multi-source ETL + one sentence -> AI -> chart.
Run from project root: streamlit run Dashboard/app.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
import duckdb
import pandas as pd
from config.sources import get_source_ids, resolve_source_paths, SOURCES, CHART_TYPES, CHART_LABELS
from Dashboard.charts import get_chart
from Ai.report import summarize


def _get_db_stats(db_path: str, table: str, columns_str: str) -> dict:
    """Sidebar DB overview: use duckdb directly to avoid cached module signature issues."""
    try:
        conn = duckdb.connect(db_path)
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()
        return {"row_count": row_count, "table": table, "db_path": db_path, "columns": columns_str}
    except Exception:
        return {"row_count": 0, "table": table, "db_path": db_path, "columns": columns_str}


def _get_schema(db_path: str, table: str) -> list:
    try:
        conn = duckdb.connect(db_path)
        schema = conn.execute(f"DESCRIBE {table}").fetchall()
        conn.close()
        return schema
    except Exception:
        return []


def _get_table_preview(db_path: str, table: str, limit: int = 200):
    try:
        conn = duckdb.connect(db_path)
        df = conn.execute(f"SELECT * FROM {table} LIMIT {limit}").fetchdf()
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


def _run_query(
    dimension: str,
    metric: str,
    db_path: str,
    table: str,
    dimensions_list: list,
    metrics_list: list,
    date_column: str,
    breakdown_dimension: str = None,
    breakdown_by_category: bool = False,
):
    """Run aggregation query in DuckDB. Returns (df, sql_str). Implemented here to avoid cached Ai.query signature issues."""
    if dimension not in dimensions_list:
        dimension = dimensions_list[0]
    if metric not in metrics_list:
        metric = metrics_list[0]
    group_col = date_column if dimension == "date" else dimension
    conn = duckdb.connect(db_path)
    try:
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
        return df, sql
    finally:
        conn.close()


def fallback_plan(user_message: str, source_cfg: dict) -> dict:
    """When Ollama is not available, pick dimension/metric/chart from keywords."""
    msg = user_message.lower()
    dims = source_cfg["dimensions"]
    metrics = source_cfg["metrics"]
    dim_labels = source_cfg["dimension_labels"]
    met_labels = source_cfg["metric_labels"]
    by_time = "by time" in msg or "over time" in msg
    dim = dims[0]
    for d in dims:
        if d in msg or (dim_labels.get(d, d).lower() in msg):
            dim = d
            break
    if by_time:
        dim = "date"
    met = metrics[0]
    for m in metrics:
        if m in msg or (met_labels.get(m, m).lower() in msg):
            met = m
            break
    chart = "bar"
    if "trend" in msg or "time" in msg or "over time" in msg:
        chart = "line"
    if "pie" in msg or "share" in msg or "proportion" in msg:
        chart = "pie"
    out = {"dimension": dim, "metric": met, "chart_type": chart}
    if by_time:
        out["by_time_breakdown"] = True
    return out


def _session_key(suffix: str, source_id: str) -> str:
    return f"{suffix}_{source_id}"


def main():
    st.set_page_config(page_title="AI Data Dashboard", layout="wide")

    source_ids = get_source_ids()

    with st.sidebar:
        st.subheader("Data source")
        selected_id = st.selectbox(
            "Select data source",
            options=source_ids,
            format_func=lambda x: SOURCES[x]["name"],
            key="source_selector",
        )
        cfg = resolve_source_paths(selected_id)

        st.subheader("ETL")
        if st.button("Run ETL for this source", key="run_etl_btn"):
            try:
                from ETL.run_etl import run
                run(selected_id)
                st.success("ETL completed")
            except Exception as e:
                st.error(str(e))

        st.subheader("Database overview")
        try:
            stats = _get_db_stats(cfg["db_path"], cfg["table"], ", ".join(cfg["columns"]))
            st.write("**Engine:** DuckDB (local file)")
            st.write("**Path:**", f"`{cfg['db_rel']}`")
            st.write("**Table:**", stats["table"])
            st.write("**Total rows:**", f"{stats['row_count']:,}")
            st.write("**Columns:**", stats["columns"])
        except Exception as e:
            st.warning(f"DB not loaded: {e}. Click \"Run ETL for this source\" first.")

    st.title("Say what you want to analyze")
    st.caption("e.g. sales by category, profit trend over time, quantity by region")
    with st.expander("Pipeline flow", expanded=True):
        st.markdown(
            f"**CSV** (`{cfg['csv_rel']}`) → **ETL** (clean & load) → **DuckDB** (`{cfg['db_rel']}`) → "
            "**Your words** → **AI** (Ollama) → **SQL** → **Chart**"
        )

    # Chart hints
    dim_hint = " / ".join(cfg["dimension_labels"].get(d, d) for d in cfg["dimensions"])
    met_hint = " / ".join(cfg["metric_labels"].get(m, m) for m in cfg["metrics"])
    chart_hint = ", ".join(CHART_LABELS.get(c, c) for c in CHART_TYPES)
    st.info(f"**Charts you can request:** by {dim_hint} for {met_hint}; supported: {chart_hint}.")

    with st.expander("View DuckDB data (schema + raw data preview)", expanded=False):
        try:
            schema = _get_schema(cfg["db_path"], cfg["table"])
            if schema:
                st.subheader("Table schema")
                st.caption(f"Table: **{cfg['table']}**")
                st.dataframe(
                    [{"Column": row[0], "Type": row[1]} for row in schema],
                    use_container_width=True,
                    hide_index=True,
                )
                st.subheader("Data preview (first 200 rows)")
                preview = _get_table_preview(cfg["db_path"], cfg["table"], 200)
                st.dataframe(preview, use_container_width=True, height=300)
            else:
                st.warning("Cannot read schema. Run ETL first.")
        except Exception as e:
            st.warning(f"DuckDB not ready: {e}. Run ETL first.")

    user_input = st.text_input("Your request", placeholder="e.g. sales by category", key="user_input")
    last_fig_key = _session_key("last_fig", selected_id)
    last_summary_key = _session_key("last_summary", selected_id)
    last_sql_key = _session_key("last_sql", selected_id)
    last_df_key = _session_key("last_df", selected_id)

    if not user_input:
        if last_fig_key in st.session_state:
            st.plotly_chart(st.session_state[last_fig_key], use_container_width=True)
            st.write(st.session_state.get(last_summary_key, ""))
        else:
            st.info("Type what you want to analyze (e.g. sales by category, profit trend over time) and click Generate chart.")
        st.stop()

    if st.button("Generate chart", type="primary"):
        plan_cache_key = f"plan_{selected_id}_{user_input.strip().lower()}"
        plan = st.session_state.get(plan_cache_key) if isinstance(st.session_state.get(plan_cache_key), dict) else None
        if plan and plan.get("dimension") and plan.get("metric") and plan.get("chart_type"):
            pass
        else:
            plan = None
            with st.spinner("AI is thinking..."):
                try:
                    from Ai.prompt import build_prompt
                    from Ai.llm import call_ollama, parse_json_from_response
                    if callable(build_prompt):
                        prompt = build_prompt(
                            user_input,
                            dimensions=cfg["dimensions"],
                            metrics=cfg["metrics"],
                            dimension_labels=cfg["dimension_labels"],
                            metric_labels=cfg["metric_labels"],
                            columns_description=", ".join(cfg["columns"]),
                        )
                        response = call_ollama(prompt)
                        plan = parse_json_from_response(response)
                except Exception as e:
                    st.warning(f"Ollama not reached ({e}). Using fallback.")
                if not plan or not plan.get("dimension"):
                    plan = fallback_plan(user_input, cfg)
                st.session_state[plan_cache_key] = plan

        dimension = plan.get("dimension", cfg["dimensions"][0])
        metric = plan.get("metric", cfg["metrics"][0])
        chart_type = plan.get("chart_type", CHART_TYPES[0])
        by_time_breakdown = bool(plan.get("by_time_breakdown", False))

        with st.spinner("Querying data..."):
            try:
                df, sql = _run_query(
                    dimension,
                    metric,
                    cfg["db_path"],
                    cfg["table"],
                    cfg["dimensions"],
                    cfg["metrics"],
                    cfg["date_column"],
                    breakdown_dimension=cfg.get("breakdown_dimension"),
                    breakdown_by_category=by_time_breakdown,
                )
            except Exception as e:
                st.error(f"Query failed: {e}. Run ETL for this source first.")
                st.stop()

        if df is None or df.empty:
            st.info("No data for this selection.")
            st.stop()

        met_label = cfg["metric_labels"].get(metric, metric)
        dim_label = cfg["dimension_labels"].get(dimension, dimension)
        if by_time_breakdown:
            title = f"{met_label} by time (by {cfg.get('breakdown_dimension', 'category')})"
        else:
            title = f"{met_label} by {dim_label}"
        fig = get_chart(df, chart_type, title)
        st.session_state[last_fig_key] = fig
        st.session_state[last_summary_key] = summarize(df)
        st.session_state[last_sql_key] = sql
        st.session_state[last_df_key] = df

        st.plotly_chart(fig, use_container_width=True)
        st.write(summarize(df))

        with st.expander("Generated SQL"):
            st.code(sql, language="sql")
        with st.expander("Query result (raw data)"):
            st.dataframe(df, use_container_width=True)

    elif last_fig_key in st.session_state:
        st.plotly_chart(st.session_state[last_fig_key], use_container_width=True)
        st.write(st.session_state.get(last_summary_key, ""))
        if last_sql_key in st.session_state:
            with st.expander("Generated SQL"):
                st.code(st.session_state[last_sql_key], language="sql")
        if last_df_key in st.session_state:
            with st.expander("Query result (raw data)"):
                st.dataframe(st.session_state[last_df_key], use_container_width=True)


if __name__ == "__main__":
    main()
