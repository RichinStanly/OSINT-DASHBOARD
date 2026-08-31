"""
Pydantic schemas used for validating data as it flows between collectors,
analysis modules, and the database layer. Keeping these separate from the
SQLAlchemy models lets collectors produce plain, validated data structures
without needing a live DB session.
"""
from __future__ import annotations

import datetime as dt
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

ConfidenceLevel = Literal["confirmed", "inferred", "uncertain"]
EntityType = Literal["PERSON", "ORG", "PRODUCT", "TECH", "LOCATION", "EVENT", "OTHER"]
SourceType = Literal["wikipedia", "news", "web"]
ResearchDepth = Literal["quick", "standard", "deep"]


class CollectedSource(BaseModel):
    """A single normalized piece of content collected from any source module."""

    title: str
    url: str
    domain: str = ""
    source_type: SourceType = "web"
    published_at: Optional[dt.datetime] = None
    raw_text: str = ""
    summary: str = ""
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError(f"Invalid URL scheme: {v}")
        return v

    @field_validator("title")
    @classmethod
    def non_empty_title(cls, v: str) -> str:
        v = v.strip()
        return v if v else "Untitled Source"


class ExtractedEntity(BaseModel):
    name: str
    entity_type: EntityType
    frequency: int = 1
    source_indices: list[int] = Field(default_factory=list)


class ExtractedRelationship(BaseModel):
    source_entity: str
    target_entity: str
    relationship_type: str = "related_to"
    confidence: ConfidenceLevel = "inferred"
    weight: float = 1.0
    evidence_source_indices: list[int] = Field(default_factory=list)


class ExtractedEvent(BaseModel):
    event_date: dt.datetime
    date_precision: Literal["day", "month", "year"] = "day"
    description: str
    source_index: Optional[int] = None
    confidence: ConfidenceLevel = "inferred"


class ExtractedTopic(BaseModel):
    label: str
    frequency: int = 1
    related_entities: list[str] = Field(default_factory=list)
    source_indices: list[int] = Field(default_factory=list)


class ResearchRequest(BaseModel):
    subject: str = Field(min_length=2, max_length=255)
    depth: ResearchDepth = "standard"

    @field_validator("subject")
    @classmethod
    def clean_subject(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Subject cannot be empty")
        return v
