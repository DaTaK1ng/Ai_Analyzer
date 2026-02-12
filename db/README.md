# db — database folder (the one we use)

This project uses **only this folder** (`db/`) for the DuckDB file. There is no `database` folder in the design.

- **Empty until you run ETL.** Run once from project root:
  ```bash
  python etl/run_etl.py
  ```
- After that, `db/app.duckdb` will appear here. The dashboard and AI query this file.

If you have a **database** folder elsewhere in the project, it is not used; you can delete it.
