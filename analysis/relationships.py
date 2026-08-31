"""
Relationship extraction.

Builds entity-to-entity relationships using sentence-level co-occurrence:
if two entities appear in the same sentence across source text, we infer
a relationship between them. This is a standard, explainable, and fully
local (no external API) approach appropriate for an educational OSINT tool.

Confidence levels:
- "confirmed": entities co-occur in the same sentence in 2+ distinct sources
- "inferred": entities co-occur in the same sentence in exactly 1 source
- "uncertain": entities only co-occur at the document (not sentence) level
"""
from __future__ import annotations

import re
from collections import defaultdict
from itertools import combinations

from core.schemas import CollectedSource, ExtractedEntity, ExtractedRelationship

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if len(s.strip()) > 5]


def extract_relationships(
    sources: list[CollectedSource],
    entities: list[ExtractedEntity],
    max_relationships: int = 60,
) -> list[ExtractedRelationship]:
    """Infer relationships between the top entities based on co-occurrence."""

    if len(entities) < 2:
        return []

                                                                        
                                         
    top_entities = entities[:40]
    entity_names = {e.name for e in top_entities}

                                                                             
    sentence_co_occurrence: dict[tuple[str, str], set[int]] = defaultdict(set)
                                                                                  
    doc_co_occurrence: dict[tuple[str, str], set[int]] = defaultdict(set)

    for idx, source in enumerate(sources):
        text = f"{source.title}. {source.raw_text}"
        if not text.strip():
            continue

        present_in_doc = {name for name in entity_names if name in text}
        for a, b in combinations(sorted(present_in_doc), 2):
            doc_co_occurrence[(a, b)].add(idx)

        for sentence in _split_sentences(text):
            present = {name for name in entity_names if name in sentence}
            for a, b in combinations(sorted(present), 2):
                sentence_co_occurrence[(a, b)].add(idx)

    relationships: list[ExtractedRelationship] = []

    for (a, b), src_ids in sentence_co_occurrence.items():
        confidence = "confirmed" if len(src_ids) >= 2 else "inferred"
        relationships.append(
            ExtractedRelationship(
                source_entity=a,
                target_entity=b,
                relationship_type="associated_with",
                confidence=confidence,                          
                weight=float(len(src_ids)),
                evidence_source_indices=sorted(src_ids),
            )
        )

                                                                             
                                                
    handled_pairs = set(sentence_co_occurrence.keys())
    for (a, b), src_ids in doc_co_occurrence.items():
        if (a, b) in handled_pairs:
            continue
        relationships.append(
            ExtractedRelationship(
                source_entity=a,
                target_entity=b,
                relationship_type="mentioned_alongside",
                confidence="uncertain",
                weight=float(len(src_ids)) * 0.5,
                evidence_source_indices=sorted(src_ids),
            )
        )

    relationships.sort(key=lambda r: r.weight, reverse=True)
    return relationships[:max_relationships]
