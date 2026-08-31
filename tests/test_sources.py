"""Tests for source deduplication and URL validation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from collectors.base import get_domain, is_valid_url
from core.pipeline import _deduplicate_sources
from core.schemas import CollectedSource


def test_is_valid_url_accepts_http_https():
    assert is_valid_url("https://example.com/page") is True
    assert is_valid_url("http://example.com") is True


def test_is_valid_url_rejects_bad_schemes():
    assert is_valid_url("ftp://example.com") is False
    assert is_valid_url("not a url") is False
    assert is_valid_url("") is False


def test_get_domain_strips_www():
    assert get_domain("https://www.example.com/page") == "example.com"
    assert get_domain("https://sub.example.com/page") == "sub.example.com"


def test_deduplicate_sources_by_url():
    sources = [
        CollectedSource(title="A", url="https://example.com/x", domain="example.com", relevance_score=0.5),
        CollectedSource(title="A dup", url="https://example.com/x", domain="example.com", relevance_score=0.9),
        CollectedSource(title="B", url="https://example.com/y", domain="example.com", relevance_score=0.3),
    ]
    deduped = _deduplicate_sources(sources)
    assert len(deduped) == 2
                                               
    match = [s for s in deduped if s.url == "https://example.com/x"][0]
    assert match.relevance_score == 0.9


def test_collected_source_rejects_invalid_url():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        CollectedSource(title="Bad", url="not-a-url", domain="")


def test_collected_source_defaults_empty_title():
    source = CollectedSource(title="   ", url="https://example.com", domain="example.com")
    assert source.title == "Untitled Source"
