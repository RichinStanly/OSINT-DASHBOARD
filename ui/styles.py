"""
Custom CSS injected into the Streamlit app to give it a professional,
dark "intelligence platform" look rather than the default Streamlit theme.
"""
from __future__ import annotations

import streamlit as st

from config.settings import settings


def inject_custom_css() -> None:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {settings.THEME_BACKGROUND};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {settings.THEME_SECONDARY_BG};
            border-right: 1px solid #30363D;
        }}

        h1, h2, h3, h4 {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            letter-spacing: -0.01em;
        }}

        h1 {{
            font-weight: 700;
            color: {settings.THEME_TEXT};
        }}

        
        div[data-testid="stMetric"] {{
            background-color: {settings.THEME_SECONDARY_BG};
            border: 1px solid #30363D;
            border-radius: 10px;
            padding: 16px 18px;
        }}
        div[data-testid="stMetricLabel"] {{
            color: {settings.THEME_MUTED};
        }}

        
        .stButton > button {{
            background-color: {settings.THEME_PRIMARY};
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
        }}
        .stButton > button:hover {{
            background-color: #4A7BD8;
            color: white;
        }}

        
        button[data-baseweb="tab"] {{
            font-weight: 600;
        }}

        
        .osint-card {{
            background-color: {settings.THEME_SECONDARY_BG};
            border: 1px solid #30363D;
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 10px;
        }}
        .osint-card:hover {{
            border-color: {settings.THEME_PRIMARY};
        }}

        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-right: 6px;
        }}
        .badge-confirmed {{ background-color: rgba(63,185,80,0.15); color: {settings.THEME_SUCCESS}; }}
        .badge-inferred {{ background-color: rgba(210,153,34,0.15); color: {settings.THEME_WARNING}; }}
        .badge-uncertain {{ background-color: rgba(139,148,158,0.15); color: {settings.THEME_MUTED}; }}
        .badge-demo {{ background-color: rgba(248,81,73,0.15); color: {settings.THEME_DANGER}; }}
        .badge-type {{ background-color: rgba(91,141,239,0.15); color: {settings.THEME_PRIMARY}; }}

        .muted-text {{ color: {settings.THEME_MUTED}; font-size: 0.85rem; }}

        a {{ color: {settings.THEME_PRIMARY}; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
