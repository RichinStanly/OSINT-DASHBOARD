"""Tests for analysis.timeline extraction."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analysis.timeline import extract_timeline
from core.schemas import CollectedSource


def _make_source(text: str) -> CollectedSource:
    return CollectedSource(
        title="Doc", url="https://example.com/y", domain="example.com",
        source_type="web", raw_text=text,
    )


def test_extract_timeline_finds_full_date():
    sources = [_make_source("The company was founded on March 5, 2019 in Austin.")]
    events = extract_timeline(sources)
    assert len(events) >= 1
    assert events[0].event_date.year == 2019
    assert events[0].event_date.month == 3
    assert events[0].event_date.day == 5
    assert events[0].date_precision == "day"


def test_extract_timeline_finds_year_only():
    sources = [_make_source("In 2015, the organization began operations.")]
    events = extract_timeline(sources)
    assert len(events) >= 1
    assert events[0].event_date.year == 2015


def test_extract_timeline_empty_text():
    events = extract_timeline([_make_source("")])
    assert events == []


def test_extract_timeline_sorted_chronologically():
    sources = [_make_source("Founded in 2020. Expanded operations in 2015. Went public in 2022.")]
    events = extract_timeline(sources)
    dates = [e.event_date for e in events]
    assert dates == sorted(dates)


def test_extract_timeline_rejects_invalid_years():
    sources = [_make_source("The report references the year 3050 in a hypothetical scenario.")]
    events = extract_timeline(sources)
    assert all(e.event_date.year <= 2027 for e in events)
