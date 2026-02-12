"""
Multi-data-source config. Each source: CSV path, DB path, table, columns, dimensions, metrics.
Paths are relative to project root; call resolve_source_paths() to get absolute paths.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chart types are shared across sources
CHART_TYPES = ["bar", "line", "pie"]
CHART_LABELS = {"bar": "Bar chart", "line": "Line chart", "pie": "Pie chart"}

SOURCES = {
    "sales": {
        "name": "Sales (Retail)",
        "csv_rel": "data/raw/sales.csv",
        "db_rel": "db/app.duckdb",
        "table": "analytics",
        "date_column": "date",
        "breakdown_dimension": "category",  # for "by time" line chart
        "columns": ["date", "category", "region", "sub_category", "product", "sales", "quantity", "profit", "discount"],
        "dimensions": ["category", "region", "sub_category", "date"],
        "metrics": ["sales", "quantity", "profit"],
        "dimension_labels": {"category": "Category", "region": "Region", "sub_category": "Sub-category", "date": "Date"},
        "metric_labels": {"sales": "Sales", "quantity": "Quantity", "profit": "Profit"},
    },
    "events": {
        "name": "Events (Web)",
        "csv_rel": "data/raw/events.csv",
        "db_rel": "db/events.duckdb",
        "table": "events",
        "date_column": "event_date",
        "breakdown_dimension": "channel",
        "columns": ["event_date", "country", "device_type", "channel", "event_name", "sessions", "conversions", "revenue"],
        "dimensions": ["country", "device_type", "channel", "event_name", "date"],
        "metrics": ["sessions", "conversions", "revenue"],
        "dimension_labels": {"country": "Country", "device_type": "Device", "channel": "Channel", "event_name": "Event", "date": "Date"},
        "metric_labels": {"sessions": "Sessions", "conversions": "Conversions", "revenue": "Revenue"},
    },
}


def resolve_source_paths(source_id: str) -> dict:
    """Return a copy of the source config with csv_path and db_path as absolute paths."""
    if source_id not in SOURCES:
        raise KeyError(f"Unknown source: {source_id}")
    cfg = dict(SOURCES[source_id])
    cfg["csv_path"] = os.path.join(ROOT, cfg["csv_rel"])
    cfg["db_path"] = os.path.join(ROOT, cfg["db_rel"])
    return cfg


def get_source_ids():
    return list(SOURCES.keys())
