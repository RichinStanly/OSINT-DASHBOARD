"""
Wikipedia collector.

Uses Wikipedia's public REST API (no key required) to:
- search for pages matching the research subject
- fetch page summaries and full extracts
- pull related/linked pages for additional context

This is the most reliable free source in the app since it is stable,
well-structured, and permits automated access via its API.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from collectors.base import fetch_json
from core.schemas import CollectedSource

WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_REST_SUMMARY = "https://en.wikipedia.org/api/rest_v1/page/summary/"


def search_wikipedia(query: str, limit: int = 5) -> list[str]:
    """Return a list of matching Wikipedia page titles for a query."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
    }
    data = fetch_json(WIKI_API, params=params)
    if not data:
        return []
    results = data.get("query", {}).get("search", [])
    return [item["title"] for item in results]


def fetch_page_summary(title: str) -> Optional[dict]:
    """Fetch the REST summary (short extract + metadata) for a page title."""
    url = WIKI_REST_SUMMARY + title.replace(" ", "_")
    return fetch_json(url)


def fetch_page_full_extract(title: str) -> Optional[str]:
    """Fetch the full plain-text extract of a Wikipedia page."""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "titles": title,
        "format": "json",
    }
    data = fetch_json(WIKI_API, params=params)
    if not data:
        return None
    pages = data.get("query", {}).get("pages", {})
    for _, page in pages.items():
        return page.get("extract")
    return None


def collect(subject: str, max_pages: int = 3) -> list[CollectedSource]:
    """Collect Wikipedia sources related to the subject.

    Returns a list of CollectedSource, best-effort. Any single failed
    page is skipped rather than aborting the whole collection.
    """
    sources: list[CollectedSource] = []

    titles = search_wikipedia(subject, limit=max_pages)
    if not titles:
        return sources

    for i, title in enumerate(titles[:max_pages]):
        try:
            summary = fetch_page_summary(title)
            if not summary or summary.get("type") == "disambiguation":
                continue

            extract = fetch_page_full_extract(title) or summary.get("extract", "")
            page_url = summary.get("content_urls", {}).get("desktop", {}).get("page")
            if not page_url:
                page_url = f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"

                                                                        
                                                                           
                                                                         
            relevance = 1.0 if i == 0 else max(0.4, 0.9 - i * 0.15)

            sources.append(
                CollectedSource(
                    title=summary.get("title", title),
                    url=page_url,
                    domain="en.wikipedia.org",
                    source_type="wikipedia",
                    published_at=None,
                    raw_text=extract or "",
                    summary=summary.get("extract", ""),
                    relevance_score=relevance,
                )
            )
        except Exception:
                                                      
            continue

    return sources
