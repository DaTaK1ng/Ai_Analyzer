import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(ROOT, "data", "raw", "sales.csv")
DB_PATH = os.path.join(ROOT, "db", "app.duckdb")
TABLE_NAME = "analytics"

# Logical column names (must match CSV headers or COLUMN_MAPPING)
COLUMNS = ["date", "category", "region", "sub_category", "product", "sales", "quantity", "profit", "discount"]
