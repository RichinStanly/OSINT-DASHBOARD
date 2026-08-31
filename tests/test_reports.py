"""Tests for reports.exporter generation."""
import datetime as dt
import json
import sys
import zipfile
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reports import exporter

INVESTIGATION = {
    "id": 1, "subject": "Test Subject", "name": "Test Investigation",
    "depth": "standard", "is_demo": False, "status": "completed",
    "created_at": dt.datetime(2024, 1, 1), "updated_at": dt.datetime(2024, 1, 2),
}
SOURCES = [
    {"id": 1, "title": "Source One", "url": "https://example.com/1", "domain": "example.com",
     "source_type": "web", "published_at": dt.datetime(2024, 1, 1), "collected_at": dt.datetime(2024, 1, 1),
     "raw_text": "text", "summary": "summary", "relevance_score": 0.9, "quality_score": 0.8,
     "corroboration_count": 1, "is_demo": False},
]
ENTITIES = [{"id": 1, "name": "Acme", "entity_type": "ORG", "frequency": 3, "source_ids": "1"}]
RELATIONSHIPS = [{"id": 1, "source_entity": "Acme", "target_entity": "Beta", "relationship_type": "related_to",
                   "confidence": "confirmed", "weight": 2.0, "evidence_source_ids": "1"}]
EVENTS = [{"id": 1, "event_date": dt.datetime(2024, 1, 1), "date_precision": "day",
           "description": "Something happened", "source_id": 1, "confidence": "confirmed"}]
TOPICS = [{"id": 1, "label": "Growth", "frequency": 2, "related_entities": "Acme", "source_ids": "1"}]
REPORT = {
    "id": 1, "executive_summary": "Summary text",
    "key_findings": json.dumps(["Finding one"]),
    "major_events": json.dumps(["2024-01-01: Event"]),
    "relationships_summary": json.dumps(["Acme <-> Beta"]),
    "emerging_themes": json.dumps(["Growth"]),
    "source_notes": "notes", "limitations": "limitations text",
    "generated_at": dt.datetime(2024, 1, 2),
}


def test_export_json_produces_valid_json():
    result = exporter.export_json(INVESTIGATION, SOURCES, ENTITIES, RELATIONSHIPS, EVENTS, TOPICS, REPORT)
    parsed = json.loads(result)
    assert parsed["investigation"]["subject"] == "Test Subject"
    assert len(parsed["sources"]) == 1
    assert len(parsed["entities"]) == 1


def test_export_csv_bundle_produces_valid_zip():
    result = exporter.export_csv_bundle(SOURCES, ENTITIES, RELATIONSHIPS, EVENTS, TOPICS)
    zf = zipfile.ZipFile(BytesIO(result))
    names = zf.namelist()
    assert "sources.csv" in names
    assert "entities.csv" in names
    content = zf.read("sources.csv").decode("utf-8")
    assert "Source One" in content


def test_export_markdown_contains_key_sections():
    md = exporter.export_markdown(INVESTIGATION, SOURCES, ENTITIES, RELATIONSHIPS, EVENTS, TOPICS, REPORT)
    assert "# Research Report" in md
    assert "## Executive Summary" in md
    assert "## Key Findings" in md
    assert "Acme" in md


def test_export_markdown_without_report():
    md = exporter.export_markdown(INVESTIGATION, SOURCES, ENTITIES, RELATIONSHIPS, EVENTS, TOPICS, None)
    assert "# Research Report" in md
    assert "## Key Entities" in md
