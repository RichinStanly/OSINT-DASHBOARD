"""
Timeline visualization: renders extracted events as an interactive
horizontal scatter/strip chart, colored by confidence level.
"""
from __future__ import annotations

import plotly.graph_objects as go

from config.settings import settings

CONFIDENCE_COLORS = {
    "confirmed": "#3FB950",
    "inferred": "#D29922",
    "uncertain": "#8B949E",
}


def render_timeline_figure(events: list[dict]) -> go.Figure:
    """Render a chronological timeline of events as an interactive Plotly figure."""
    if not events:
        fig = go.Figure()
        fig.add_annotation(
            text="No timeline events detected yet.",
            showarrow=False, font=dict(color=settings.THEME_MUTED, size=14),
        )
        fig.update_layout(
            plot_bgcolor=settings.THEME_SECONDARY_BG,
            paper_bgcolor=settings.THEME_SECONDARY_BG,
            height=300,
        )
        return fig

    fig = go.Figure()

    for confidence, color in CONFIDENCE_COLORS.items():
        subset = [e for e in events if e["confidence"] == confidence]
        if not subset:
            continue
        fig.add_trace(
            go.Scatter(
                x=[e["event_date"] for e in subset],
                y=[0 for _ in subset],
                mode="markers",
                marker=dict(size=14, color=color, line=dict(width=1, color="rgba(255,255,255,0.25)")),
                name=confidence.capitalize(),
                text=[e["description"][:120] for e in subset],
                hovertemplate="%{x|%Y-%m-%d}<br>%{text}<extra></extra>",
            )
        )

    fig.update_layout(
        plot_bgcolor=settings.THEME_SECONDARY_BG,
        paper_bgcolor=settings.THEME_SECONDARY_BG,
        font=dict(color=settings.THEME_TEXT),
        yaxis=dict(visible=False, range=[-1, 1]),
        xaxis=dict(title="Date", gridcolor="#30363D"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        height=280,
        margin=dict(l=10, r=10, t=40, b=40),
    )
    return fig
