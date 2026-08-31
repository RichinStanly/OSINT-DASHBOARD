"""
Source quality scoring.

Computes a composite 0-1 quality score for each collected source based on:
- source type (Wikipedia and established news generally score higher)
- presence of a publication date (undated sources are less verifiable)
- content length (very thin pages score lower)
- corroboration (how many other sources cover overlapping content)

This is a heuristic, transparent scoring system — not a claim of
ground-truth reliability — and is surfaced to the user as such.
"""
from __future__ import annotations

from core.schemas import CollectedSource

TYPE_BASE_SCORE = {
    "wikipedia": 0.75,
    "news": 0.65,
    "web": 0.5,
}

REPUTABLE_NEWS_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "npr.org",
    "nytimes.com", "wsj.com", "theguardian.com", "bloomberg.com",
    "economist.com", "ft.com",
}


def score_source(source: CollectedSource, corroboration_count: int = 0) -> float:
    """Compute a 0-1 quality score for a single source."""
    score = TYPE_BASE_SCORE.get(source.source_type, 0.4)

    if source.domain in REPUTABLE_NEWS_DOMAINS:
        score += 0.15

    if source.published_at is not None:
        score += 0.1

    content_len = len(source.raw_text or "")
    if content_len > 2000:
        score += 0.1
    elif content_len < 300:
        score -= 0.15

    score += min(corroboration_count, 3) * 0.03

    return max(0.0, min(1.0, round(score, 3)))


def compute_corroboration(sources: list[CollectedSource]) -> list[int]:
    """Approximate corroboration by counting how many other sources share
    significant title-word overlap with each source (a proxy for covering
    the same underlying story/topic)."""
    title_word_sets = [
        {w.lower() for w in s.title.split() if len(w) > 3} for s in sources
    ]
    counts = []
    for i, words_i in enumerate(title_word_sets):
        count = 0
        for j, words_j in enumerate(title_word_sets):
            if i == j or not words_i or not words_j:
                continue
            overlap = words_i & words_j
            if len(overlap) >= 2:
                count += 1
        counts.append(count)
    return counts
