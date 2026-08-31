"""
Entity extraction.

Prefers spaCy's small English model (free, local, no API required) for
proper named-entity recognition. If spaCy or its model isn't installed,
falls back to a lightweight regex/heuristic extractor so the app still
works out of the box without any extra downloads.
"""
from __future__ import annotations

import re
from collections import defaultdict

from core.schemas import CollectedSource, ExtractedEntity

_NLP = None
_SPACY_TRIED = False

                                                        
SPACY_LABEL_MAP = {
    "PERSON": "PERSON",
    "ORG": "ORG",
    "PRODUCT": "PRODUCT",
    "GPE": "LOCATION",
    "LOC": "LOCATION",
    "FAC": "LOCATION",
    "EVENT": "EVENT",
    "NORP": "ORG",
    "WORK_OF_ART": "PRODUCT",
}

                                                                       
STOPWORDS = {
    "The", "This", "That", "These", "Those", "It", "They", "He", "She",
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
}

TECH_KEYWORDS_PATTERN = re.compile(
    r"\b([A-Z][a-zA-Z0-9]*(?:\s[A-Z][a-zA-Z0-9]*){0,3})\b"
)


def _load_spacy():
    """Lazily load spaCy, returning None if unavailable. Cached across calls."""
    global _NLP, _SPACY_TRIED
    if _SPACY_TRIED:
        return _NLP
    _SPACY_TRIED = True
    try:
        import spacy                
        try:
            _NLP = spacy.load("en_core_web_sm")
        except OSError:
            _NLP = None
    except ImportError:
        _NLP = None
    return _NLP


def _extract_with_spacy(text: str, nlp) -> list[tuple[str, str]]:
    doc = nlp(text[:100000])                               
    found = []
    for ent in doc.ents:
        label = SPACY_LABEL_MAP.get(ent.label_)
        if label is None:
            continue
        name = ent.text.strip()
        if len(name) < 2 or name in STOPWORDS:
            continue
        found.append((name, label))
    return found


def _extract_with_regex(text: str) -> list[tuple[str, str]]:
    """Heuristic fallback: capitalized word sequences are treated as
    candidate ORG/PRODUCT/OTHER entities. Much cruder than spaCy but
    keeps the app functional without any model download."""
    found = []
    for match in TECH_KEYWORDS_PATTERN.finditer(text):
        name = match.group(1).strip()
        if len(name) < 2 or name in STOPWORDS:
            continue
        if name.isupper() and len(name) <= 5:
            found.append((name, "ORG"))                            
        else:
            found.append((name, "OTHER"))
    return found


def extract_entities(sources: list[CollectedSource]) -> list[ExtractedEntity]:
    """Extract and aggregate named entities across all collected sources.

    Frequency counts and per-entity source indices are aggregated so the
    UI can show "mentioned in N sources" and link back to evidence.
    """
    nlp = _load_spacy()
    counts: dict[tuple[str, str], int] = defaultdict(int)
    source_map: dict[tuple[str, str], set[int]] = defaultdict(set)

    for idx, source in enumerate(sources):
        text = f"{source.title}. {source.raw_text}"
        if not text.strip():
            continue

        if nlp is not None:
            pairs = _extract_with_spacy(text, nlp)
        else:
            pairs = _extract_with_regex(text)

        for name, etype in pairs:
            key = (name, etype)
            counts[key] += 1
            source_map[key].add(idx)

    entities: list[ExtractedEntity] = []
    for (name, etype), freq in counts.items():
                                                                         
                                                              
        if freq < 1:
            continue
        entities.append(
            ExtractedEntity(
                name=name,
                entity_type=etype,                          
                frequency=freq,
                source_indices=sorted(source_map[(name, etype)]),
            )
        )

                                                                   
    entities.sort(key=lambda e: e.frequency, reverse=True)

                                                                       
                                                                           
    return entities[:150]
