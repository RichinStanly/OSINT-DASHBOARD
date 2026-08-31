"""
Reusable Streamlit UI components: badges, source cards, confidence
indicators, and the demo-data banner.
"""
from __future__ import annotations

import datetime as dt

import streamlit as st


def confidence_badge(confidence: str) -> str:
    label = confidence.capitalize()
    return f'<span class="badge badge-{confidence}">{label}</span>'


def type_badge(label: str) -> str:
    return f'<span class="badge badge-type">{label}</span>'


def demo_banner() -> None:
    st.markdown(
        '<div style="background-color:rgba(248,81,73,0.12); border:1px solid #F85149; '
        'border-radius:8px; padding:10px 16px; margin-bottom:16px;">'
        '<span class="badge badge-demo">DEMO DATA</span>'
        '<span style="color:#F85149; font-weight:600;"> This investigation uses sample data '
        "for demonstration purposes, not live research results.</span></div>",
        unsafe_allow_html=True,
    )


def format_date(value) -> str:
    if value is None:
        return "Unknown date"
    if isinstance(value, dt.datetime):
        return value.strftime("%Y-%m-%d")
    return str(value)


def render_source_card(source: dict) -> None:
    """Render a single source card.

    The expander label below embeds `source['id']` (the DB primary key) as
    an invisible zero-width-character suffix so every card gets a distinct
    label. This matters because Streamlit identifies expanders by their
    label text, and every source card would otherwise render the exact
    same label ("View extracted content"). Rendering two or more source
    cards in the same run would then raise a StreamlitDuplicateElementId
    error. This approach works across all Streamlit versions.
    """
    pub_date = format_date(source.get("published_at"))
    quality_pct = int(round(source.get("quality_score", 0) * 100))
    relevance_pct = int(round(source.get("relevance_score", 0) * 100))

    with st.container():
        st.markdown(
            f"""
            <div class="osint-card">
                <div style="display:flex; justify-content:space-between; align-items:baseline;">
                    <div style="font-weight:600; font-size:1.02rem;">{source['title']}</div>
                    <div class="muted-text">{source['domain']}</div>
                </div>
                <div class="muted-text" style="margin-top:2px;">
                    {type_badge(source['source_type'])} Published: {pub_date} &nbsp;•&nbsp;
                    Quality: {quality_pct}% &nbsp;•&nbsp; Relevance: {relevance_pct}%
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
                                                                          
                                                                           
                                              
        unique_suffix = "".join("\u200c" if bit == "1" else "\u200b" for bit in format(int(source["id"]), "b"))
        with st.expander(f"View extracted content{unique_suffix}"):
            st.write(source.get("summary") or source.get("raw_text", "")[:800] or "No content extracted.")
            st.markdown(f"[Open original source]({source['url']})")


def render_entity_row(entity: dict, source_count: int) -> None:
    st.markdown(
        f"""
        <div class="osint-card" style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="font-weight:600;">{entity['name']}</span>
                {type_badge(entity['entity_type'])}
            </div>
            <div class="muted-text">{entity['frequency']} mention(s) across {source_count} source(s)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def coverage_score(source_count: int, entity_count: int, relationship_count: int) -> tuple[int, str]:
    """A simple heuristic 0-100 'research coverage' score used on the dashboard.
    Not a claim of factual completeness — just a rough indicator of how much
    structured signal was extracted relative to typical investigation sizes."""
    score = 0
    score += min(source_count, 20) * 2                 
    score += min(entity_count, 30) * 1.2                
    score += min(relationship_count, 20) * 1.2            
    score = min(100, round(score))

    if score >= 70:
        label = "Strong coverage"
    elif score >= 40:
        label = "Moderate coverage"
    else:
        label = "Limited coverage"
    return int(score), label
