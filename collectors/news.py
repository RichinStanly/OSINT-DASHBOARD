"""
News collector.

Uses NewsAPI.org's free developer tier if an API key is configured
(NEWSAPI_KEY in .env). This is entirely optional: if no key is present,
`collect()` simply returns an empty list and the rest of the app
continues normally using Wikipedia and general web sources.

We never require a paid API for the application to function.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from collectors.base import fetch_json, get_domain
from config.settings import settings
from core.schemas import CollectedSource

NEWSAPI_URL = "https://newsapi.org/v2/everything"


def _parse_date(value: Optional[str]) -> Optional[dt.datetime]:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def collect(subject: str, max_items: int = 10) -> list[CollectedSource]:
    """Collect recent news articles mentioning the subject.

    Returns an empty list (not an error) if NEWSAPI_KEY is not configured,
    the request fails, or no articles are found — the app must keep working
    without this source.
    """
    if not settings.NEWSAPI_KEY:
        return []

    params = {
        "q": subject,
        "apiKey": settings.NEWSAPI_KEY,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": max_items,
    }
    data = fetch_json(NEWSAPI_URL, params=params)
    if not data or data.get("status") != "ok":
        return []

    sources: list[CollectedSource] = []
    articles = data.get("articles", [])
    for i, article in enumerate(articles[:max_items]):
        url = article.get("url", "")
        if not url:
            continue
        try:
            sources.append(
                CollectedSource(
                    title=article.get("title") or "Untitled Article",
                    url=url,
                    domain=get_domain(url),
                    source_type="news",
                    published_at=_parse_date(article.get("publishedAt")),
                    raw_text=(article.get("content") or article.get("description") or ""),
                    summary=article.get("description") or "",
                    relevance_score=max(0.3, 0.9 - i * 0.05),
                )
            )
        except Exception:
            continue

    return sources
