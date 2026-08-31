"""
Database engine and session management.

Provides a single SQLAlchemy engine bound to the local SQLite file, a
session factory, and small CRUD helper functions used throughout the app.
Keeping DB access centralized here means the UI layer never talks to
SQLAlchemy directly.
"""
from __future__ import annotations

import datetime as dt
from contextlib import contextmanager
from typing import Iterator, Optional

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings
from core.models import (
    Base,
    Entity,
    EntityRelationship,
    Investigation,
    Report,
    Source,
    TimelineEvent,
    Topic,
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all tables if they do not already exist. Safe to call repeatedly."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Iterator[Session]:
    """Context-managed session with automatic commit/rollback."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


                                                                       
                            
                                                                       

def create_investigation(subject: str, name: Optional[str] = None, depth: str = "standard", is_demo: bool = False) -> int:
    with get_session() as session:
        inv = Investigation(
            subject=subject.strip(),
            name=(name or subject).strip(),
            depth=depth,
            is_demo=is_demo,
            status="created",
        )
        session.add(inv)
        session.flush()
        return inv.id


def list_investigations() -> list[dict]:
    with get_session() as session:
        rows = session.query(Investigation).order_by(Investigation.updated_at.desc()).all()
        return [
            {
                "id": r.id,
                "subject": r.subject,
                "name": r.name,
                "depth": r.depth,
                "is_demo": r.is_demo,
                "status": r.status,
                "created_at": r.created_at,
                "updated_at": r.updated_at,
            }
            for r in rows
        ]


def get_investigation(investigation_id: int) -> Optional[dict]:
    with get_session() as session:
        r = session.get(Investigation, investigation_id)
        if r is None:
            return None
        return {
            "id": r.id,
            "subject": r.subject,
            "name": r.name,
            "depth": r.depth,
            "is_demo": r.is_demo,
            "status": r.status,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        }


def rename_investigation(investigation_id: int, new_name: str) -> None:
    with get_session() as session:
        inv = session.get(Investigation, investigation_id)
        if inv is not None:
            inv.name = new_name.strip()
            inv.updated_at = dt.datetime.utcnow()


def update_investigation_status(investigation_id: int, status: str) -> None:
    with get_session() as session:
        inv = session.get(Investigation, investigation_id)
        if inv is not None:
            inv.status = status
            inv.updated_at = dt.datetime.utcnow()


def delete_investigation(investigation_id: int) -> None:
    with get_session() as session:
        inv = session.get(Investigation, investigation_id)
        if inv is not None:
            session.execute(delete(Investigation).where(Investigation.id == investigation_id))


                                                                       
                                                                
                                                                     
                                                                     
                                                                       

def get_sources(investigation_id: int) -> list[dict]:
    with get_session() as session:
        rows = (
            session.query(Source)
            .filter(Source.investigation_id == investigation_id)
            .order_by(Source.relevance_score.desc())
            .all()
        )
        return [
            {
                "id": r.id, "title": r.title, "url": r.url, "domain": r.domain,
                "source_type": r.source_type, "published_at": r.published_at,
                "collected_at": r.collected_at, "raw_text": r.raw_text,
                "summary": r.summary, "relevance_score": r.relevance_score,
                "quality_score": r.quality_score, "corroboration_count": r.corroboration_count,
                "is_demo": r.is_demo,
            }
            for r in rows
        ]


def get_entities(investigation_id: int) -> list[dict]:
    with get_session() as session:
        rows = (
            session.query(Entity)
            .filter(Entity.investigation_id == investigation_id)
            .order_by(Entity.frequency.desc())
            .all()
        )
        return [
            {
                "id": r.id, "name": r.name, "entity_type": r.entity_type,
                "frequency": r.frequency, "source_ids": r.source_ids,
            }
            for r in rows
        ]


def get_relationships(investigation_id: int) -> list[dict]:
    with get_session() as session:
        rows = (
            session.query(EntityRelationship)
            .filter(EntityRelationship.investigation_id == investigation_id)
            .order_by(EntityRelationship.weight.desc())
            .all()
        )
        return [
            {
                "id": r.id, "source_entity": r.source_entity, "target_entity": r.target_entity,
                "relationship_type": r.relationship_type, "confidence": r.confidence,
                "weight": r.weight, "evidence_source_ids": r.evidence_source_ids,
            }
            for r in rows
        ]


def get_timeline_events(investigation_id: int) -> list[dict]:
    with get_session() as session:
        rows = (
            session.query(TimelineEvent)
            .filter(TimelineEvent.investigation_id == investigation_id)
            .order_by(TimelineEvent.event_date.asc())
            .all()
        )
        return [
            {
                "id": r.id, "event_date": r.event_date, "date_precision": r.date_precision,
                "description": r.description, "source_id": r.source_id, "confidence": r.confidence,
            }
            for r in rows
        ]


def get_topics(investigation_id: int) -> list[dict]:
    with get_session() as session:
        rows = (
            session.query(Topic)
            .filter(Topic.investigation_id == investigation_id)
            .order_by(Topic.frequency.desc())
            .all()
        )
        return [
            {
                "id": r.id, "label": r.label, "frequency": r.frequency,
                "related_entities": r.related_entities, "source_ids": r.source_ids,
            }
            for r in rows
        ]


def get_report(investigation_id: int) -> Optional[dict]:
    with get_session() as session:
        r = (
            session.query(Report)
            .filter(Report.investigation_id == investigation_id)
            .order_by(Report.generated_at.desc())
            .first()
        )
        if r is None:
            return None
        return {
            "id": r.id, "executive_summary": r.executive_summary,
            "key_findings": r.key_findings, "major_events": r.major_events,
            "relationships_summary": r.relationships_summary,
            "emerging_themes": r.emerging_themes, "source_notes": r.source_notes,
            "limitations": r.limitations, "generated_at": r.generated_at,
        }
