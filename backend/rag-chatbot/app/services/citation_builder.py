"""
Citation builder service for formatting source references.
Extracts and formats citations from retrieved chunks.
"""
from typing import List
from uuid import UUID

from app.utils.logging import get_logger

logger = get_logger(__name__)


def build_citations(chunks: List[dict]) -> List[dict]:
    """
    Build citation list from retrieved chunks.

    Args:
        chunks: List of retrieved chunks with metadata

    Returns:
        List of formatted citations
    """
    try:
        citations = []

        for chunk in chunks:
            citation = {
                "chunk_id": chunk["chunk_id"],
                "chapter": chunk["chapter"],
                "section": chunk["section"],
                "url": chunk["url"],
                "confidence_score": round(chunk["confidence_score"], 2),
                "text_snippet": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
            }
            citations.append(citation)

        # Sort by confidence score descending
        citations.sort(key=lambda x: x["confidence_score"], reverse=True)

        logger.debug(
            "citations_built",
            citation_count=len(citations),
            top_score=citations[0]["confidence_score"] if citations else 0,
        )

        return citations

    except Exception as e:
        logger.error("citation_building_failed", error=str(e))
        return []


def deduplicate_citations(citations: List[dict], max_citations: int = 5) -> List[dict]:
    """
    Deduplicate citations by chapter, keeping highest scoring ones.

    Args:
        citations: List of citations
        max_citations: Maximum number of citations to return

    Returns:
        Deduplicated list of citations
    """
    seen_chapters = set()
    unique_citations = []

    for citation in citations:
        chapter = citation["chapter"]

        if chapter not in seen_chapters:
            seen_chapters.add(chapter)
            unique_citations.append(citation)

        if len(unique_citations) >= max_citations:
            break

    logger.debug(
        "citations_deduplicated",
        original_count=len(citations),
        final_count=len(unique_citations),
    )

    return unique_citations
