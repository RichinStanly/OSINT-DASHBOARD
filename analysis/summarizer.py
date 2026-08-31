"""
Research summary generation.

Default mode is fully local: a deterministic extractive summarizer that
selects the most representative sentences (via TF-IDF sentence scoring)
and structures them into an executive summary, key findings, and
limitations section. Requires no external API.

"""
from __future__ import annotations

import json
import re

from config.settings import settings
from core.schemas import (
    CollectedSource,
    ExtractedEntity,
    ExtractedEvent,
    ExtractedRelationship,
    ExtractedTopic,
)

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _top_sentences(sources: list[CollectedSource], n: int = 6) -> list[str]:
    """Rank sentences across all sources by TF-IDF score and return the top N."""
    all_sentences = []
    for s in sources:
        text = s.raw_text or s.summary
        for sentence in SENTENCE_SPLIT.split(text):
            sentence = sentence.strip()
            if 40 < len(sentence) < 400:
                all_sentences.append(sentence)

    if not all_sentences:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        matrix = vectorizer.fit_transform(all_sentences)
        scores = matrix.sum(axis=1).A1
        ranked = sorted(zip(all_sentences, scores), key=lambda x: x[1], reverse=True)
                                                                              
        picked, seen = [], set()
        for sentence, _ in ranked:
            key = sentence[:60].lower()
            if key in seen:
                continue
            seen.add(key)
            picked.append(sentence)
            if len(picked) >= n:
                break
        return picked
    except ImportError:
                                                                       
        return all_sentences[:n]


def generate_extractive_summary(
    subject: str,
    sources: list[CollectedSource],
    entities: list[ExtractedEntity],
    relationships: list[ExtractedRelationship],
    events: list[ExtractedEvent],
    topics: list[ExtractedTopic],
) -> dict:
    """Build a structured report using deterministic, source-grounded logic.

    This is the default and always-available summarization path.
    """
    top_sentences = _top_sentences(sources, n=6)
    executive_summary = (
        f"This research workspace on \"{subject}\" was compiled from "
        f"{len(sources)} publicly available source(s). "
        + (" ".join(top_sentences[:3]) if top_sentences else "Limited textual content was available to summarize.")
    )

    key_findings = top_sentences[:6] if top_sentences else [
        "Insufficient source text was collected to extract detailed findings."
    ]

    major_events = [
        f"{e.event_date.strftime('%Y-%m-%d') if e.date_precision == 'day' else e.event_date.strftime('%Y-%m')}: {e.description}"
        for e in events[:8]
    ]

    relationships_summary = [
        f"{r.source_entity} \u2194 {r.target_entity} ({r.relationship_type}, {r.confidence})"
        for r in relationships[:10]
    ]

    emerging_themes = [f"{t.label} (seen in {t.frequency} source(s))" for t in topics[:8]]

    confirmed_count = sum(1 for r in relationships if r.confidence == "confirmed")
    uncertain_count = sum(1 for r in relationships if r.confidence == "uncertain")
    source_notes = (
        f"{len(sources)} source(s) collected. "
        f"{confirmed_count} relationship(s) corroborated across multiple sources; "
        f"{uncertain_count} relationship(s) are document-level co-occurrences only "
        "and should be treated as weaker evidence."
    )

    limitations = (
        "This summary was generated automatically using extractive text analysis "
        "and co-occurrence-based relationship inference, not human verification. "
        "Entity extraction and date parsing are heuristic and may contain errors "
        "or omissions. Timeline events with 'uncertain' confidence reflect a bare "
        "year mention rather than a precise date. Always verify important claims "
        "against the original sources listed in the Sources tab before relying on them."
    )

    return {
        "executive_summary": executive_summary,
        "key_findings": json.dumps(key_findings),
        "major_events": json.dumps(major_events),
        "relationships_summary": json.dumps(relationships_summary),
        "emerging_themes": json.dumps(emerging_themes),
        "source_notes": source_notes,
        "limitations": limitations,
    }

