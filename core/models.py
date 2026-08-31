"""
SQLAlchemy ORM models for the OSINT Research Dashboard.

Everything a research session produces (sources, entities, relationships,
timeline events, topics, and reports) is persisted here, scoped to an
Investigation.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


def utcnow() -> dt.datetime:
    return dt.datetime.utcnow()


class Investigation(Base):
    """A single research session for one subject."""

    __tablename__ = "investigations"

    id = Column(Integer, primary_key=True)
    subject = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    depth = Column(String(20), nullable=False, default="standard")
    is_demo = Column(Boolean, nullable=False, default=False)
    status = Column(String(30), nullable=False, default="created")                                       
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    sources = relationship("Source", back_populates="investigation", cascade="all, delete-orphan")
    entities = relationship("Entity", back_populates="investigation", cascade="all, delete-orphan")
    relationships_ = relationship("EntityRelationship", back_populates="investigation", cascade="all, delete-orphan")
    events = relationship("TimelineEvent", back_populates="investigation", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="investigation", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="investigation", cascade="all, delete-orphan")


class Source(Base):
    """A single collected document/page/article."""

    __tablename__ = "sources"
    __table_args__ = (UniqueConstraint("investigation_id", "url", name="uq_source_investigation_url"),)

    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)

    title = Column(String(500), nullable=False)
    url = Column(String(1000), nullable=False)
    domain = Column(String(255))
    source_type = Column(String(50), default="web")                        
    published_at = Column(DateTime, nullable=True)
    collected_at = Column(DateTime, default=utcnow)

    raw_text = Column(Text, default="")
    summary = Column(Text, default="")

    relevance_score = Column(Float, default=0.0)                                 
    quality_score = Column(Float, default=0.0)                                          
    corroboration_count = Column(Integer, default=0)                                             

    is_demo = Column(Boolean, default=False)

    investigation = relationship("Investigation", back_populates="sources")


class Entity(Base):
    """An extracted named entity (person, org, product, location, etc.)."""

    __tablename__ = "entities"
    __table_args__ = (UniqueConstraint("investigation_id", "name", "entity_type", name="uq_entity_investigation_name_type"),)

    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)

    name = Column(String(255), nullable=False)
    entity_type = Column(String(50), nullable=False)                                               
    frequency = Column(Integer, default=1)
    source_ids = Column(Text, default="")                                        

    investigation = relationship("Investigation", back_populates="entities")


class EntityRelationship(Base):
    """A relationship/edge between two entities."""

    __tablename__ = "entity_relationships"

    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)

    source_entity = Column(String(255), nullable=False)
    target_entity = Column(String(255), nullable=False)
    relationship_type = Column(String(100), default="related_to")
    confidence = Column(String(20), default="inferred")                                  
    weight = Column(Float, default=1.0)
    evidence_source_ids = Column(Text, default="")

    investigation = relationship("Investigation", back_populates="relationships_")


class TimelineEvent(Base):
    """A dated event extracted from source text."""

    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)

    event_date = Column(DateTime, nullable=False)
    date_precision = Column(String(10), default="day")                    
    description = Column(Text, nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=True)
    confidence = Column(String(20), default="inferred")                                  

    investigation = relationship("Investigation", back_populates="events")


class Topic(Base):
    """A recurring theme/topic identified across sources."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)

    label = Column(String(255), nullable=False)
    frequency = Column(Integer, default=1)
    related_entities = Column(Text, default="")                                
    source_ids = Column(Text, default="")

    investigation = relationship("Investigation", back_populates="topics")


class Report(Base):
    """A generated research summary/report for an investigation."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id"), nullable=False)

    executive_summary = Column(Text, default="")
    key_findings = Column(Text, default="")                          
    major_events = Column(Text, default="")                           
    relationships_summary = Column(Text, default="")                     
    emerging_themes = Column(Text, default="")                        
    source_notes = Column(Text, default="")
    limitations = Column(Text, default="")
    generated_at = Column(DateTime, default=utcnow)

    investigation = relationship("Investigation", back_populates="reports")
