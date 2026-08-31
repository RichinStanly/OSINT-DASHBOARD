"""
Miscellaneous dashboard charts: source-type breakdown, topic frequency,
entity-type distribution, and source quality visualization.
"""
from __future__ import annotations

from collections import Counter

import plotly.graph_objects as go

from config.settings import settings

CHART_COLORS = ["#5B8DEF", "#39C5CF", "#A371F7", "#F778BA", "#FFA657", "#3FB950", "#D29922"]


def _base_layout(height: int = 300) -> dict:
    return dict(
        plot_bgcolor=settings.THEME_SECONDARY_BG,
        paper_bgcolor=settings.THEME_SECONDARY_BG,
        font=dict(color=settings.THEME_TEXT),
        height=height,
        margin=dict(l=10, r=10, t=30, b=30),
    )


def render_source_type_chart(sources: list[dict]) -> go.Figure:
    """Pie chart of source types (wikipedia / news / web)."""
    counts = Counter(s["source_type"] for s in sources)
    if not counts:
        fig = go.Figure()
        fig.update_layout(**_base_layout())
        return fig

    fig = go.Figure(
        data=[
            go.Pie(
                labels=list(counts.keys()),
                values=list(counts.values()),
                hole=0.5,
                marker=dict(colors=CHART_COLORS),
                textfont=dict(color="#0E1117"),
            )
        ]
    )
    fig.update_layout(title="Sources by Type", **_base_layout())
    return fig


def render_entity_type_chart(entities: list[dict]) -> go.Figure:
    """Bar chart of entity counts by type."""
    counts = Counter(e["entity_type"] for e in entities)
    if not counts:
        fig = go.Figure()
        fig.update_layout(**_base_layout())
        return fig

    sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    fig = go.Figure(
        data=[
            go.Bar(
                x=[k for k, _ in sorted_items],
                y=[v for _, v in sorted_items],
                marker_color=CHART_COLORS[0],
            )
        ]
    )
    fig.update_layout(
        title="Entities by Type",
        xaxis=dict(gridcolor="#30363D"),
        yaxis=dict(gridcolor="#30363D"),
        **_base_layout(),
    )
    return fig


def render_topic_frequency_chart(topics: list[dict]) -> go.Figure:
    """Horizontal bar chart of top topics by frequency."""
    if not topics:
        fig = go.Figure()
        fig.update_layout(**_base_layout())
        return fig

    top = sorted(topics, key=lambda t: t["frequency"], reverse=True)[:12]
    top = list(reversed(top))                                                 

    fig = go.Figure(
        data=[
            go.Bar(
                x=[t["frequency"] for t in top],
                y=[t["label"] for t in top],
                orientation="h",
                marker_color=CHART_COLORS[2],
            )
        ]
    )
    fig.update_layout(
        title="Top Topics",
        xaxis=dict(gridcolor="#30363D", title="Sources mentioning"),
        **_base_layout(height=400),
    )
    return fig


def render_source_quality_chart(sources: list[dict]) -> go.Figure:
    """Scatter plot of relevance vs quality score per source."""
    if not sources:
        fig = go.Figure()
        fig.update_layout(**_base_layout())
        return fig

    fig = go.Figure(
        data=[
            go.Scatter(
                x=[s["relevance_score"] for s in sources],
                y=[s["quality_score"] for s in sources],
                mode="markers",
                text=[s["title"][:60] for s in sources],
                hovertemplate="%{text}<br>Relevance: %{x:.2f}<br>Quality: %{y:.2f}<extra></extra>",
                marker=dict(size=12, color=CHART_COLORS[4], line=dict(width=1, color="rgba(255,255,255,0.25)")),
            )
        ]
    )
    fig.update_layout(
        title="Source Relevance vs. Quality",
        xaxis=dict(title="Relevance Score", range=[0, 1.05], gridcolor="#30363D"),
        yaxis=dict(title="Quality Score", range=[0, 1.05], gridcolor="#30363D"),
        **_base_layout(height=350),
    )
    return fig
