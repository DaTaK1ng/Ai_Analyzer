# Data Description

## What this dataset is

This is **retail order-level data** (superstore-style): each row is one **order line** — one product (or product type) sold on a given date, in a given region, with sales amount, quantity, profit, and discount.

- **Source**: Sample data for demo (inspired by Tableau Sample Superstore). Generated locally; no real customer data.
- **Rows**: ~8,000 order lines.
- **Time span**: 2021–2023 (about 3 years).
- **Use**: To show how AI can turn “I want to see X” into charts and reports: e.g. sales by category, profit by region, trends over time.

## Columns

| Column        | Meaning                                      | Example                    |
|---------------|----------------------------------------------|----------------------------|
| date          | Order date                                   | 2022-03-26                 |
| category      | Product category (top level)                 | Furniture, Office Supplies, Technology |
| region        | Sales region                                 | East, West, South, Central |
| sub_category  | Product sub-category                         | Chairs, Phones, Art, …     |
| product       | Product identifier                           | Product_1, Product_2, …    |
| sales         | Revenue (e.g. USD) for that line             | 3722.60                    |
| quantity      | Units sold                                   | 20                         |
| profit        | Profit for that line                         | 453.23                     |
| discount      | Discount rate (0–1)                          | 0.05                       |

## How to introduce it (English script)

Use the following when presenting:

---

**“This dataset is retail order-level data: about 8,000 rows, each row representing one order line — so one product (or product type) sold on a certain date, in one of four regions: East, West, South, and Central.**

**We have three main product categories: Furniture, Office Supplies, and Technology. Under each category there are sub-categories — for example, under Technology we have Phones, Machines, Accessories, and Copiers. For each order line we have the date, the category and sub-category, the region, the product ID, and then the business metrics: sales revenue, quantity sold, profit, and discount rate.**

**The data spans roughly 2021 to 2023, so we can look at trends over time, compare performance across regions or categories, and see how discounts relate to sales and profit. In this demo, I ask the system in natural language what I want to analyze — for example, ‘sales by category’ or ‘profit trend by region’ — and the AI drives the full pipeline: it figures out what to query, runs it against this data, and then generates the charts and a short report. So this dataset is the backbone that makes that end-to-end flow possible.”**

---

You can shorten or adapt the last sentence depending on how much you want to emphasize the AI pipeline vs. the data itself.
