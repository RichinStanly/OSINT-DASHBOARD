"""
Topic/theme extraction.

Uses scikit-learn's TfidfVectorizer over source texts to find the most
distinctive recurring terms/phrases (unigrams + bigrams) across the
collected corpus. This is a lightweight, fully local approach — no
external topic-modeling API needed — and works reasonably even on
small research corpora (a handful of sources).
"""
from __future__ import annotations

from collections import defaultdict

from core.schemas import CollectedSource, ExtractedEntity, ExtractedTopic

BASIC_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "over", "after",
    "is", "are", "was", "were", "be", "been", "being", "have", "has",
    "had", "do", "does", "did", "will", "would", "could", "should",
    "this", "that", "these", "those", "it", "its", "as", "he", "she",
    "they", "their", "his", "her", "them", "we", "our", "you", "your",
}


def extract_topics(
    sources: list[CollectedSource],
    entities: list[ExtractedEntity],
    max_topics: int = 15,
) -> list[ExtractedTopic]:
    """Identify recurring topics/themes across the collected corpus."""

    texts = [f"{s.title}. {s.raw_text}" for s in sources if (s.raw_text or s.title)]
    if len(texts) < 1:
        return []

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
    except ImportError:
        return _fallback_topics(sources, entities, max_topics)

    try:
        vectorizer = TfidfVectorizer(
            max_features=200,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.9,
        )
        matrix = vectorizer.fit_transform(texts)
        scores = matrix.sum(axis=0).A1
        terms = vectorizer.get_feature_names_out()

        term_scores = sorted(zip(terms, scores), key=lambda x: x[1], reverse=True)
    except ValueError:
        return _fallback_topics(sources, entities, max_topics)

    entity_names = [e.name for e in entities]
    topics: list[ExtractedTopic] = []
    seen_labels: set[str] = set()

    for term, score in term_scores:
        if score <= 0:
            continue
        label = term.strip()
        if len(label) < 3 or label.lower() in BASIC_STOPWORDS:
            continue
        if label.lower() in seen_labels:
            continue
        seen_labels.add(label.lower())

                                                                        
                                                   
        related_source_idx = [
            i for i, t in enumerate(texts) if label.lower() in t.lower()
        ]
        related_entities = [
            name for name in entity_names
            if any(name.lower() in texts[i].lower() for i in related_source_idx)
        ][:6]

        topics.append(
            ExtractedTopic(
                label=label.title() if label.islower() else label,
                frequency=len(related_source_idx),
                related_entities=related_entities,
                source_indices=related_source_idx,
            )
        )
        if len(topics) >= max_topics:
            break

    topics.sort(key=lambda t: t.frequency, reverse=True)
    return topics


def _fallback_topics(
    sources: list[CollectedSource],
    entities: list[ExtractedEntity],
    max_topics: int,
) -> list[ExtractedTopic]:
    """Simple word-frequency fallback if scikit-learn is unavailable."""
    word_counts: dict[str, int] = defaultdict(int)
    word_sources: dict[str, set[int]] = defaultdict(set)

    for idx, s in enumerate(sources):
        text = f"{s.title} {s.raw_text}".lower()
        for word in text.split():
            cleaned = "".join(c for c in word if c.isalnum())
            if len(cleaned) < 4 or cleaned in BASIC_STOPWORDS:
                continue
            word_counts[cleaned] += 1
            word_sources[cleaned].add(idx)

    ranked = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    entity_names = [e.name for e in entities]
    topics = []
    for word, freq in ranked[:max_topics]:
        related = [n for n in entity_names if word in n.lower()][:6]
        topics.append(
            ExtractedTopic(
                label=word.title(),
                frequency=freq,
                related_entities=related,
                source_indices=sorted(word_sources[word]),
            )
        )
    return topics
