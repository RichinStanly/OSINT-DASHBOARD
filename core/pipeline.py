"""
Research pipeline orchestrator.

Coordinates the full flow: collect sources -> score quality -> extract
entities/relationships/timeline/topics -> generate summary -> persist
everything to SQLite. Designed to run source-by-source with a progress
callback so the Streamlit UI can show live progress, and to never let a
single failed step abort the whole investigation.
"""
from __future__ import annotations

import datetime as dt
from typing import Callable, Optional

from analysis.entities import extract_entities
from analysis.relationships import extract_relationships
from analysis.source_quality import compute_corroboration, score_source
from analysis.summarizer import generate_extractive_summary
from analysis.timeline import extract_timeline
from analysis.topics import extract_topics
from collectors import news, web_sources, wikipedia
from config.settings import settings
from core import demo_data
from core.database import get_session, update_investigation_status
from core.models import Entity, EntityRelationship, Report, Source, TimelineEvent, Topic
from core.schemas import CollectedSource

ProgressCallback = Optional[Callable[[str, float], None]]


def _report_progress(callback: ProgressCallback, message: str, fraction: float) -> None:
    if callback:
        try:
            callback(message, fraction)
        except Exception:
            pass


def run_research(investigation_id: int, subject: str, depth: str, progress_callback: ProgressCallback = None) -> None:
    """Run the full research pipeline for a (non-demo) investigation."""
    update_investigation_status(investigation_id, "running")
    limits = settings.DEPTH_LIMITS.get(depth, settings.DEPTH_LIMITS["standard"])

    try:
        collected: list[CollectedSource] = []

        _report_progress(progress_callback, "Searching Wikipedia...", 0.05)
        try:
            wiki_sources = wikipedia.collect(subject, max_pages=3)
            collected.extend(wiki_sources)
        except Exception:
            pass

        _report_progress(progress_callback, "Searching news sources...", 0.20)
        try:
            news_sources = news.collect(subject, max_items=limits["max_news_items"])
            collected.extend(news_sources)
        except Exception:
            pass

        _report_progress(progress_callback, "Searching general web sources...", 0.35)
        try:
            remaining_slots = max(0, limits["max_sources"] - len(collected))
            if remaining_slots > 0:
                web_results = web_sources.collect(subject, max_pages=remaining_slots)
                collected.extend(web_results)
        except Exception:
            pass

                                                                         
        _report_progress(progress_callback, "Deduplicating sources...", 0.45)
        collected = _deduplicate_sources(collected)
        collected = collected[: limits["max_sources"]]

        if not collected:
            update_investigation_status(investigation_id, "failed")
            _report_progress(progress_callback, "No sources could be collected.", 1.0)
            return

        _report_progress(progress_callback, "Scoring source quality...", 0.5)
        corroboration_counts = compute_corroboration(collected)
        quality_scores = [
            score_source(s, corroboration_counts[i]) for i, s in enumerate(collected)
        ]

        _report_progress(progress_callback, "Extracting entities...", 0.6)
        entities = extract_entities(collected)

        _report_progress(progress_callback, "Mapping relationships...", 0.7)
        relationships = extract_relationships(collected, entities)

        _report_progress(progress_callback, "Building timeline...", 0.78)
        events = extract_timeline(collected)

        _report_progress(progress_callback, "Identifying topics...", 0.85)
        topics = extract_topics(collected, entities)

        _report_progress(progress_callback, "Generating research summary...", 0.92)
        report_data = generate_extractive_summary(subject, collected, entities, relationships, events, topics)

        _report_progress(progress_callback, "Saving results...", 0.97)
        _persist_results(
            investigation_id, collected, quality_scores, corroboration_counts,
            entities, relationships, events, topics, report_data,
        )

        update_investigation_status(investigation_id, "completed")
        _report_progress(progress_callback, "Research complete.", 1.0)

    except Exception:
        update_investigation_status(investigation_id, "failed")
        _report_progress(progress_callback, "Research failed due to an unexpected error.", 1.0)
        raise


def _deduplicate_sources(sources: list[CollectedSource]) -> list[CollectedSource]:
    seen: dict[str, CollectedSource] = {}
    for s in sources:
        existing = seen.get(s.url)
        if existing is None or s.relevance_score > existing.relevance_score:
            seen[s.url] = s
    result = list(seen.values())
    result.sort(key=lambda s: s.relevance_score, reverse=True)
    return result


def _persist_results(
    investigation_id: int,
    sources: list[CollectedSource],
    quality_scores: list[float],
    corroboration_counts: list[int],
    entities,
    relationships,
    events,
    topics,
    report_data: dict,
) -> None:
    with get_session() as session:
        source_id_by_index: dict[int, int] = {}

        for i, s in enumerate(sources):
            db_source = Source(
                investigation_id=investigation_id,
                title=s.title,
                url=s.url,
                domain=s.domain,
                source_type=s.source_type,
                published_at=s.published_at,
                raw_text=s.raw_text,
                summary=s.summary,
                relevance_score=s.relevance_score,
                quality_score=quality_scores[i],
                corroboration_count=corroboration_counts[i],
                is_demo=False,
            )
            session.add(db_source)
            session.flush()
            source_id_by_index[i] = db_source.id

        for e in entities:
            src_ids = ",".join(str(source_id_by_index[i]) for i in e.source_indices if i in source_id_by_index)
            session.add(
                Entity(
                    investigation_id=investigation_id,
                    name=e.name,
                    entity_type=e.entity_type,
                    frequency=e.frequency,
                    source_ids=src_ids,
                )
            )

        for r in relationships:
            evidence_ids = ",".join(
                str(source_id_by_index[i]) for i in r.evidence_source_indices if i in source_id_by_index
            )
            session.add(
                EntityRelationship(
                    investigation_id=investigation_id,
                    source_entity=r.source_entity,
                    target_entity=r.target_entity,
                    relationship_type=r.relationship_type,
                    confidence=r.confidence,
                    weight=r.weight,
                    evidence_source_ids=evidence_ids,
                )
            )

        for ev in events:
            session.add(
                TimelineEvent(
                    investigation_id=investigation_id,
                    event_date=ev.event_date,
                    date_precision=ev.date_precision,
                    description=ev.description,
                    source_id=source_id_by_index.get(ev.source_index) if ev.source_index is not None else None,
                    confidence=ev.confidence,
                )
            )

        for t in topics:
            src_ids = ",".join(str(source_id_by_index[i]) for i in t.source_indices if i in source_id_by_index)
            session.add(
                Topic(
                    investigation_id=investigation_id,
                    label=t.label,
                    frequency=t.frequency,
                    related_entities=",".join(t.related_entities),
                    source_ids=src_ids,
                )
            )

        session.add(
            Report(
                investigation_id=investigation_id,
                executive_summary=report_data["executive_summary"],
                key_findings=report_data["key_findings"],
                major_events=report_data["major_events"],
                relationships_summary=report_data["relationships_summary"],
                emerging_themes=report_data["emerging_themes"],
                source_notes=report_data["source_notes"],
                limitations=report_data["limitations"],
            )
        )


def load_demo_investigation(investigation_id: int) -> None:
    """Populate an investigation with the built-in demo dataset."""
    import json

    with get_session() as session:
        source_id_by_title: dict[str, int] = {}

        for s in demo_data.DEMO_SOURCES:
            db_source = Source(
                investigation_id=investigation_id,
                title=s["title"],
                url=s["url"],
                domain=s["domain"],
                source_type=s["source_type"],
                published_at=s["published_at"],
                raw_text=s["raw_text"],
                summary=s["summary"],
                relevance_score=s["relevance_score"],
                quality_score=0.8,
                corroboration_count=2,
                is_demo=True,
            )
            session.add(db_source)
            session.flush()
            source_id_by_title[s["title"]] = db_source.id

        all_source_ids = ",".join(str(v) for v in source_id_by_title.values())

        for name, etype, freq in demo_data.DEMO_ENTITIES:
            session.add(
                Entity(
                    investigation_id=investigation_id,
                    name=name,
                    entity_type=etype,
                    frequency=freq,
                    source_ids=all_source_ids,
                )
            )

        for src, tgt, rtype, confidence, weight in demo_data.DEMO_RELATIONSHIPS:
            session.add(
                EntityRelationship(
                    investigation_id=investigation_id,
                    source_entity=src,
                    target_entity=tgt,
                    relationship_type=rtype,
                    confidence=confidence,
                    weight=weight,
                    evidence_source_ids=all_source_ids,
                )
            )

        for event_date, description, confidence, source_title in demo_data.DEMO_EVENTS:
            session.add(
                TimelineEvent(
                    investigation_id=investigation_id,
                    event_date=event_date,
                    date_precision="day",
                    description=description,
                    source_id=source_id_by_title.get(source_title),
                    confidence=confidence,
                )
            )

        for label, freq, related in demo_data.DEMO_TOPICS:
            session.add(
                Topic(
                    investigation_id=investigation_id,
                    label=label,
                    frequency=freq,
                    related_entities=",".join(related),
                    source_ids=all_source_ids,
                )
            )

        r = demo_data.DEMO_REPORT
        session.add(
            Report(
                investigation_id=investigation_id,
                executive_summary=r["executive_summary"],
                key_findings=json.dumps(r["key_findings"]),
                major_events=json.dumps(r["major_events"]),
                relationships_summary=json.dumps(r["relationships_summary"]),
                emerging_themes=json.dumps(r["emerging_themes"]),
                source_notes=r["source_notes"],
                limitations=r["limitations"],
            )
        )

    update_investigation_status(investigation_id, "completed")
