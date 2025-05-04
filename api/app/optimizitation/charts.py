"""charts.py – Plot generation
=============================
All user‑facing figures are built here so that visual logic is separated from
numerical logic.
"""

import plotly.express as px
import pandas as pd

__all__ = ["cumulative_return_chart"]


def cumulative_return_chart(cum_pct: pd.Series, title: str) -> "plotly.graph_objs.Figure":
    """Generate an interactive Plotly line chart from a cumulative‑percent Series."""
    if cum_pct.name is None:
        cum_pct = cum_pct.rename("Cumulative Return (%)")

    df = cum_pct.to_frame().reset_index()
    df.columns = ["Date", "Cumulative Return (%)"]

    fig = px.line(
        df,
        x="Date",
        y="Cumulative Return (%)",
        title=title,
        markers=True,
        template="plotly_white",
    )
    fig.update_yaxes(tickformat=".2f")
    return fig
