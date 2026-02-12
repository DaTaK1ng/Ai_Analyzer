"""
Fetch or generate sample data into data/raw/sales.csv.
Schema: date, category, region, sub_category, product, sales, quantity, profit, discount.
Run from project root: python scripts/download_data.py
"""
import os
import random
import csv
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "data", "raw", "sales.csv")
OUT_DIR = os.path.dirname(OUT_PATH)

# Public CSV (Superstore-style); more columns for richer charts
URL = "https://raw.githubusercontent.com/brandonruggles/Tableau-Datasets/master/Sample%20-%20Superstore.csv"
URL_COLUMN_MAP = {
    "Order Date": "date",
    "Category": "category",
    "Region": "region",
    "Sub-Category": "sub_category",
    "Sales": "sales",
    "Quantity": "quantity",
    "Profit": "profit",
    "Discount": "discount",
}


def download_csv():
    try:
        import urllib.request
        req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", errors="replace")
        reader = csv.DictReader(text.splitlines())
        rows = []
        for row in reader:
            new = {}
            for old_name, new_name in URL_COLUMN_MAP.items():
                if old_name in row and row[old_name].strip() != "":
                    new[new_name] = row[old_name].strip()
            if len(new) == len(URL_COLUMN_MAP):
                try:
                    float(new.get("sales", 0))
                    float(new.get("quantity", 0))
                    float(new.get("profit", 0))
                    float(new.get("discount", 0))
                except (ValueError, TypeError):
                    continue
                rows.append(new)
        if len(rows) < 500:
            return False
        os.makedirs(OUT_DIR, exist_ok=True)
        with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(URL_COLUMN_MAP.values()))
            w.writeheader()
            w.writerows(rows)
        print(f"Downloaded {len(rows)} rows -> {OUT_PATH}")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False


def generate_sample():
    os.makedirs(OUT_DIR, exist_ok=True)
    categories = ["Furniture", "Office Supplies", "Technology"]
    sub_categories = {
        "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
        "Office Supplies": ["Paper", "Binders", "Storage", "Appliances", "Art", "Envelopes"],
        "Technology": ["Phones", "Machines", "Accessories", "Copiers"],
    }
    regions = ["East", "West", "South", "Central"]
    products = [f"Product_{i}" for i in range(1, 41)]
    start = datetime(2021, 1, 1)
    rows = []
    n = 8000
    for _ in range(n):
        d = start + timedelta(days=random.randint(0, 1000))
        cat = random.choice(categories)
        sub = random.choice(sub_categories[cat])
        reg = random.choice(regions)
        prod = random.choice(products)
        qty = random.randint(1, 20)
        unit_price = round(random.uniform(15, 500), 2)
        sales = round(qty * unit_price, 2)
        discount = round(random.uniform(0, 0.25), 2)
        profit = round(sales * (1 - discount) * random.uniform(0.05, 0.35), 2)
        rows.append({
            "date": d.strftime("%Y-%m-%d"),
            "category": cat,
            "region": reg,
            "sub_category": sub,
            "product": prod,
            "sales": sales,
            "quantity": qty,
            "profit": profit,
            "discount": discount,
        })
    fieldnames = ["date", "category", "region", "sub_category", "product", "sales", "quantity", "profit", "discount"]
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Generated {len(rows)} rows -> {OUT_PATH}")


if __name__ == "__main__":
    if not download_csv():
        generate_sample()
