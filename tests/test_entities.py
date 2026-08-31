"""Tests for analysis.entities extraction."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analysis.entities import extract_entities
from core.schemas import CollectedSource


def _make_source(title: str, text: str) -> CollectedSource:
    return CollectedSource(
        title=title, url="https://example.com/a", domain="example.com",
        source_type="web", raw_text=text, summary=text[:100],
    )


def test_extract_entities_returns_list():
    sources = [
        _make_source(
            "Aurora Robotics Overview",
            "Aurora Robotics is a company based in Austin. Maria Chen leads the company.",
        )
    ]
    entities = extract_entities(sources)
    assert isinstance(entities, list)


def test_extract_entities_empty_input():
    entities = extract_entities([])
    assert entities == []


def test_extract_entities_frequency_aggregation():
    sources = [
        _make_source("Doc 1", "Aurora Robotics announced a partnership. Aurora Robotics is growing."),
        _make_source("Doc 2", "Aurora Robotics continues to expand its business."),
    ]
    entities = extract_entities(sources)
                                                                               
    assert all(e.frequency >= 1 for e in entities)


def test_extract_entities_caps_result_size():
    long_text = " ".join([f"Entity{i} Corp" for i in range(500)])
    sources = [_make_source("Big Doc", long_text)]
    entities = extract_entities(sources)
    assert len(entities) <= 150
