"""
Vector search service for retrieving relevant chunks from Qdrant.
Supports general mode (query only) and selected-text mode (hybrid/filtered retrieval).
Uses local sentence-transformers embeddings (384 dimensions, completely free, no API key).
"""
from typing import List, Optional

from app.clients.qdrant_client import qdrant_client
from app.clients.local_embedding_client import local_embedding_client
from app.utils.logging import get_logger
from app.utils.metrics import RETRIEVAL_DURATION

logger = get_logger(__name__)


async def search_similar_chunks(
    query: str,
    top_k: int = 8,
    score_threshold: float = 0.40,
    selected_text: Optional[str] = None,
) -> List[dict]:
    """
    Search for similar chunks in Qdrant.

    Args:
        query: User's question
        top_k: Number of results to return (default 8)
        score_threshold: Minimum similarity score (default 0.40)
        selected_text: Optional selected text for hybrid/filtered search

    Returns:
        List of chunks with scores and metadata
    """
    with RETRIEVAL_DURATION.time():
        try:
            # Generate embedding for query using local model
            print(f"[VECTOR_SEARCH] Generating embedding for query: '{query}'")
            query_embedding = await local_embedding_client.generate_embedding(query)
            print(f"[VECTOR_SEARCH] ✓ Embedding generated: {len(query_embedding)} dimensions, sample: {query_embedding[:3]}")

            # If selected_text provided, use hybrid approach
            # For MVP, we'll do weighted search (can enhance with filters later)
            if selected_text:
                # Generate embedding for selected text too using local model
                selected_embedding = await local_embedding_client.generate_embedding(selected_text)

                # Weighted average: 70% query, 30% selected text
                # This helps focus on relevant context while staying flexible
                combined_embedding = [
                    0.7 * q + 0.3 * s
                    for q, s in zip(query_embedding, selected_embedding)
                ]

                results = await qdrant_client.search_similar(
                    query_vector=combined_embedding,
                    limit=top_k,
                    score_threshold=score_threshold,
                )

                logger.info(
                    "hybrid_search_complete",
                    results_count=len(results),
                    query_length=len(query),
                    selected_text_length=len(selected_text),
                )
            else:
                # Standard semantic search
                print(f"[VECTOR_SEARCH] Searching Qdrant with threshold={score_threshold}, limit={top_k}")
                results = await qdrant_client.search_similar(
                    query_vector=query_embedding,
                    limit=top_k,
                    score_threshold=score_threshold,
                )
                print(f"[VECTOR_SEARCH] ✓ Qdrant returned {len(results)} results")
                if results:
                    print(f"[VECTOR_SEARCH] Top scores: {[round(r.score, 3) for r in results[:3]]}")
                else:
                    print(f"[VECTOR_SEARCH] ⚠️ WARNING: No results! Trying with threshold=0.3...")
                    # Debug: try lower threshold
                    results_debug = await qdrant_client.search_similar(
                        query_vector=query_embedding,
                        limit=top_k,
                        score_threshold=0.3,
                    )
                    print(f"[VECTOR_SEARCH] With threshold=0.3: {len(results_debug)} results")
                    if results_debug:
                        print(f"[VECTOR_SEARCH] 💡 SOLUTION: Lower score_threshold from {score_threshold} to 0.4")

                logger.info(
                    "semantic_search_complete",
                    results_count=len(results),
                    query_length=len(query),
                )

            # Format results for downstream use
            chunks = []
            for result in results:
                chunk = {
                    "chunk_id": str(result.id),
                    "text": result.payload.get("text_content", ""),
                    "chapter": result.payload.get("chapter_path", ""),
                    "section": result.payload.get("section_title", ""),
                    "url": result.payload.get("url_path", ""),
                    "confidence_score": float(result.score),
                }
                chunks.append(chunk)

            logger.debug(
                "chunks_formatted",
                chunk_count=len(chunks),
                avg_score=sum(c["confidence_score"] for c in chunks) / len(chunks) if chunks else 0,
            )

            return chunks

        except Exception as e:
            logger.error("vector_search_failed", error=str(e), query_length=len(query))
            raise
