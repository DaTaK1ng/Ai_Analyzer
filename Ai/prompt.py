"""
Build prompt for LLM: user message + table schema + analysis options -> JSON (dimension, metric, chart_type).
Accepts per-source dimensions, metrics, and labels.
"""
from config.sources import CHART_TYPES, CHART_LABELS


def build_prompt(
    user_message: str,
    dimensions: list,
    metrics: list,
    dimension_labels: dict,
    metric_labels: dict,
    columns_description: str,
) -> str:
    dims = ",".join(dimensions)
    mets = ",".join(metrics)
    charts = ",".join(CHART_TYPES)
    return f"""Table columns: {columns_description}. Dimensions: {dims}. Metrics: {mets}. Chart types: {charts}.
User: "{user_message}"
If user wants trend over time or "by time", use dimension "date", chart_type "line", "by_time_breakdown":true.
Reply ONLY with JSON: {{"dimension":"...","metric":"...","chart_type":"...","by_time_breakdown":true/false}}
"""
