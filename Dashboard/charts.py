"""
Plot bar, line, pie from DataFrame (dim/value or date/value).
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def plot_bar(df: pd.DataFrame, title: str = "Chart", x_col: str = "dim", y_col: str = "value") -> go.Figure:
    if "date" in df.columns:
        x_col, y_col = "date", "value"
    else:
        x_col = "dim" if "dim" in df.columns else df.columns[0]
        y_col = "value" if "value" in df.columns else df.columns[1]
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_line(df: pd.DataFrame, title: str = "Chart", x_col: str = "date", y_col: str = "value") -> go.Figure:
    if "date" not in df.columns and "dim" in df.columns:
        x_col, y_col = "dim", "value"
        color_col = None
    else:
        x_col = "date" if "date" in df.columns else df.columns[0]
        y_col = "value" if "value" in df.columns else df.columns[1]
        # By time breakdown: one line per category
        color_col = "category" if "category" in df.columns else None
    if color_col:
        fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title, markers=True)
    else:
        fig = px.line(df, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_pie(df: pd.DataFrame, title: str = "Chart", name_col: str = "dim", value_col: str = "value") -> go.Figure:
    name_col = "dim" if "dim" in df.columns else df.columns[0]
    value_col = "value" if "value" in df.columns else df.columns[1]
    fig = px.pie(df, names=name_col, values=value_col, title=title)
    return fig


def get_chart(df: pd.DataFrame, chart_type: str, title: str) -> go.Figure:
    if chart_type == "bar":
        return plot_bar(df, title=title)
    if chart_type == "line":
        return plot_line(df, title=title)
    if chart_type == "pie":
        return plot_pie(df, title=title)
    return plot_bar(df, title=title)
