"""Tests for analysis.relationships extraction."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analysis.relationships import extract_relationships
from core.schemas import CollectedSource, ExtractedEntity


def _make_source(text: str) -> CollectedSource:
    return CollectedSource(
        title="Doc", url="https://example.com/x", domain="example.com",
        source_type="web", raw_text=text,
    )


def test_extract_relationships_requires_two_entities():
    entities = [ExtractedEntity(name="Solo", entity_type="ORG", frequency=1)]
    sources = [_make_source("Solo is a company.")]
    rels = extract_relationships(sources, entities)
    assert rels == []


def test_extract_relationships_finds_cooccurrence():
    sources = [_make_source("Acme Corp partnered with Globex Inc on a new initiative.")]
    entities = [
        ExtractedEntity(name="Acme Corp", entity_type="ORG", frequency=1, source_indices=[0]),
        ExtractedEntity(name="Globex Inc", entity_type="ORG", frequency=1, source_indices=[0]),
    ]
    rels = extract_relationships(sources, entities)
    assert len(rels) >= 1
    pair = {rels[0].source_entity, rels[0].target_entity}
    assert pair == {"Acme Corp", "Globex Inc"}
    assert rels[0].confidence in ("confirmed", "inferred", "uncertain")


def test_extract_relationships_empty_sources():
    entities = [
        ExtractedEntity(name="A", entity_type="ORG", frequency=1),
        ExtractedEntity(name="B", entity_type="ORG", frequency=1),
    ]
    rels = extract_relationships([], entities)
    assert rels == []
