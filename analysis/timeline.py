"""
Timeline extraction.

Scans source text for date-like expressions using dateparser/regex and
pairs each detected date with the sentence it appears in, producing a
chronological list of candidate events. This is inherently noisy (natural
language date extraction always is), so every event is tagged with a
confidence level and always links back to its source sentence.
"""
from __future__ import annotations

import datetime as dt
import re

from core.schemas import CollectedSource, ExtractedEvent

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")

MONTHS = (
    "January|February|March|April|May|June|July|August|September|"
    "October|November|December"
)

                                                                            
DATE_PATTERNS = [
    (re.compile(rf"\b({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})\b"), "day"),
    (re.compile(rf"\b({MONTHS})\s+(\d{{4}})\b"), "month"),
    (re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b"), "day"),
    (re.compile(r"\bin\s+(\d{4})\b"), "year"),
    (re.compile(r"\b(20\d{2})\b"), "year"),
]

MONTH_LOOKUP = {
    name: i + 1
    for i, name in enumerate(
        [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December",
        ]
    )
}


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if len(s.strip()) > 10]


def _parse_date_match(pattern_idx: int, match: re.Match) -> dt.datetime | None:
    try:
        if pattern_idx == 0:                   
            month_name, day, year = match.groups()
            return dt.datetime(int(year), MONTH_LOOKUP[month_name], int(day))
        if pattern_idx == 1:              
            month_name, year = match.groups()
            return dt.datetime(int(year), MONTH_LOOKUP[month_name], 1)
        if pattern_idx == 2:            
            year, month, day = match.groups()
            return dt.datetime(int(year), int(month), int(day))
        if pattern_idx == 3:             
            (year,) = match.groups()
            return dt.datetime(int(year), 1, 1)
        if pattern_idx == 4:             
            (year,) = match.groups()
            return dt.datetime(int(year), 1, 1)
    except (ValueError, KeyError):
        return None
    return None


def extract_timeline(sources: list[CollectedSource], max_events: int = 50) -> list[ExtractedEvent]:
    """Extract candidate timeline events from all collected source text."""

    current_year = dt.datetime.utcnow().year
    events: list[ExtractedEvent] = []
    seen: set[tuple[str, str]] = set()                                     

    for idx, source in enumerate(sources):
        text = source.raw_text or source.summary
        if not text:
            continue

        for sentence in _split_sentences(text):
            matched_date = None
            precision = "year"

            for pattern_idx, (pattern, prec) in enumerate(DATE_PATTERNS):
                m = pattern.search(sentence)
                if m:
                    parsed = _parse_date_match(pattern_idx, m)
                    if parsed and 1900 <= parsed.year <= current_year + 1:
                        matched_date = parsed
                        precision = prec
                        break

            if matched_date is None:
                continue

            description = sentence.strip()
            if len(description) > 300:
                description = description[:297] + "..."

            dedup_key = (matched_date.isoformat()[:10], description[:80])
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            confidence = "confirmed" if precision == "day" else "inferred"
            if precision == "year":
                confidence = "uncertain"

            events.append(
                ExtractedEvent(
                    event_date=matched_date,
                    date_precision=precision,                          
                    description=description,
                    source_index=idx,
                    confidence=confidence,                          
                )
            )

    events.sort(key=lambda e: e.event_date)
    return events[:max_events]
