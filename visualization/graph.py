"""
Interactive relationship graph visualization.

Builds a NetworkX graph from extracted entities/relationships and renders
it as an interactive Plotly figure with a spring layout. Node size reflects
entity frequency; edge color/style reflects relationship confidence.
"""
from __future__ import annotations

import networkx as nx
import plotly.graph_objects as go

from config.settings import settings

CONFIDENCE_COLORS = {
    "confirmed": "#3FB950",
    "inferred": "#D29922",
    "uncertain": "#8B949E",
}

ENTITY_TYPE_COLORS = {
    "PERSON": "#F778BA",
    "ORG": "#5B8DEF",
    "PRODUCT": "#39C5CF",
    "TECH": "#A371F7",
    "LOCATION": "#FFA657",
    "EVENT": "#F85149",
    "OTHER": "#8B949E",
}


def build_graph(entities: list[dict], relationships: list[dict]) -> nx.Graph:
    """Build a NetworkX graph from entity/relationship dicts (as stored in DB)."""
    g = nx.Graph()

    entity_types = {e["name"]: e["entity_type"] for e in entities}
    entity_freq = {e["name"]: e["frequency"] for e in entities}

    for rel in relationships:
        src, tgt = rel["source_entity"], rel["target_entity"]
        if src not in g:
            g.add_node(src, entity_type=entity_types.get(src, "OTHER"), frequency=entity_freq.get(src, 1))
        if tgt not in g:
            g.add_node(tgt, entity_type=entity_types.get(tgt, "OTHER"), frequency=entity_freq.get(tgt, 1))
        g.add_edge(
            src, tgt,
            relationship_type=rel["relationship_type"],
            confidence=rel["confidence"],
            weight=rel.get("weight", 1.0),
        )

    return g


def render_graph_figure(entities: list[dict], relationships: list[dict]) -> go.Figure:
    """Render the entity relationship graph as an interactive Plotly figure."""
    g = build_graph(entities, relationships)

    if g.number_of_nodes() == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No relationships available yet. Run research to populate the graph.",
            showarrow=False, font=dict(color=settings.THEME_MUTED, size=14),
        )
        fig.update_layout(
            plot_bgcolor=settings.THEME_SECONDARY_BG,
            paper_bgcolor=settings.THEME_SECONDARY_BG,
            height=500,
        )
        return fig

    pos = nx.spring_layout(g, k=0.6, iterations=50, seed=42)

                                                                   
    edge_traces = []
    for confidence, color in CONFIDENCE_COLORS.items():
        edge_x, edge_y = [], []
        for u, v, data in g.edges(data=True):
            if data.get("confidence") != confidence:
                continue
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]
        if edge_x:
            edge_traces.append(
                go.Scatter(
                    x=edge_x, y=edge_y, mode="lines",
                    line=dict(width=1.5, color=color),
                    hoverinfo="none",
                    name=confidence.capitalize(),
                    showlegend=True,
                )
            )

                   
    node_x, node_y, node_text, node_color, node_size, node_hover = [], [], [], [], [], []
    for node, data in g.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
        node_color.append(ENTITY_TYPE_COLORS.get(data.get("entity_type", "OTHER"), "#8B949E"))
        freq = data.get("frequency", 1)
        node_size.append(12 + min(freq, 20) * 2)
        node_hover.append(f"{node}<br>Type: {data.get('entity_type', 'OTHER')}<br>Mentions: {freq}")

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=node_text, textposition="top center",
        textfont=dict(size=10, color=settings.THEME_TEXT),
        hovertext=node_hover, hoverinfo="text",
        marker=dict(size=node_size, color=node_color, line=dict(width=1, color="rgba(255,255,255,0.19)")),
        showlegend=False,
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        plot_bgcolor=settings.THEME_SECONDARY_BG,
        paper_bgcolor=settings.THEME_SECONDARY_BG,
        font=dict(color=settings.THEME_TEXT),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=10, r=10, t=40, b=10),
        height=550,
    )
    return fig
