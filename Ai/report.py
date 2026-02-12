"""
Generate a short text summary from DataFrame stats (optional; can use LLM later).
"""
import pandas as pd


def summarize(df: pd.DataFrame, metric: str = "value") -> str:
    if df is None or df.empty:
        return "No data."
    total = df[metric].sum()
    top = df.nlargest(3, metric)
    parts = [f"Total: {total:,.2f}."]
    if "dim" in df.columns:
        for _, row in top.iterrows():
            parts.append(f"{row['dim']}: {row[metric]:,.2f}")
    elif "date" in df.columns:
        parts.append(f"Time range: {df['date'].iloc[0]} to {df['date'].iloc[-1]}.")
    return " ".join(parts)
