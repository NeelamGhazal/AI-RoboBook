"""
RAG pipeline orchestrator.
Coordinates retrieval, context building, and generation.
"""
import time
from typing import AsyncGenerator, List, Optional, Tuple

from app.services.citation_builder import build_citations, deduplicate_citations
from app.services.llm import build_conversation_history, generate_response, generate_response_stream
from app.services.vector_search import search_similar_chunks
from app.utils.logging import get_logger
from app.utils.metrics import EMBEDDING_DURATION, RETRIEVAL_DURATION, GENERATION_DURATION

logger = get_logger(__name__)


async def execute_rag_pipeline(
    question: str,
    conversation_history: List = None,
    selected_text: Optional[str] = None,
    top_k: int = 8,
    stream: bool = False,
) -> Tuple[str, List[dict], dict]:
    """
    Execute full RAG pipeline: retrieve → augment → generate.

    Args:
        question: User's question
        conversation_history: Previous messages from DB
        selected_text: Optional selected text for context
        top_k: Number of chunks to retrieve
        stream: Whether to stream response

    Returns:
        Tuple of (response, citations, metadata)
    """
    start_time = time.time()
    metadata = {}

    try:
        # Stage 1: Vector Search & Retrieval
        retrieval_start = time.time()

        # Check if user selected text
        if selected_text:
            # Selected text mode: Use selected text as PRIMARY context
            logger.info(
                "selected_text_mode",
                question_length=len(question),
                selected_text_length=len(selected_text),
            )
            print(f"[RAG] Selected text mode - using provided context ({len(selected_text)} chars)")
            print(f"[RAG] Question: '{question}'")

            # Create synthetic chunk from selected text
            chunks = [{
                "chunk_id": "selected_text",
                "text": selected_text,
                "chapter": "Selected Text",
                "section": "User Selection",
                "url": "#",
                "confidence_score": 1.0,  # Maximum confidence for user-selected text
            }]

            # Optionally search for related content to supplement (but don't require it)
            try:
                related_chunks = await search_similar_chunks(
                    query=question,
                    top_k=2,  # Just 2 related chunks to supplement
                    selected_text=None,  # Don't use hybrid search
                )
                if related_chunks:
                    print(f"[RAG] Found {len(related_chunks)} related chunks to supplement")
                    chunks.extend(related_chunks[:2])
                else:
                    print(f"[RAG] No related chunks found - using only selected text")
            except Exception as e:
                print(f"[RAG] Related search failed: {e} - using only selected text")
                # Continue with just selected text

            metadata["chunks_retrieved"] = len(chunks)
            metadata["selected_text_used"] = True

        else:
            # General mode: Vector search only
            chunks = await search_similar_chunks(
                query=question,
                top_k=top_k,
                selected_text=None,
            )

            metadata["chunks_retrieved"] = len(chunks)
            metadata["selected_text_used"] = False

            # Only show error if NO selected text AND no search results
            if not chunks:
                logger.warning("no_chunks_retrieved", question_length=len(question))
                return (
                    "I couldn't find relevant information in the textbook to answer your question.",
                    [],
                    metadata
                )

        retrieval_time = time.time() - retrieval_start
        metadata["retrieval_time_ms"] = int(retrieval_time * 1000)

        # Stage 2: Build Citations
        citations = build_citations(chunks)
        citations = deduplicate_citations(citations, max_citations=5)

        metadata["avg_confidence"] = round(
            sum(c["confidence_score"] for c in citations) / len(citations),
            2
        ) if citations else 0

        # Stage 3: Build Conversation Context
        formatted_history = []
        if conversation_history:
            formatted_history = build_conversation_history(conversation_history)

        # Stage 4: Generate Response
        generation_start = time.time()

        if stream:
            # For streaming, we can't return the full response here
            # The endpoint will handle streaming
            response = ""  # Placeholder
            token_count = 0
        else:
            response, token_count = await generate_response(
                question=question,
                chunks=chunks,
                conversation_history=formatted_history,
            )

        generation_time = time.time() - generation_start
        metadata["generation_time_ms"] = int(generation_time * 1000)
        metadata["token_count"] = token_count

        # Total time
        total_time = time.time() - start_time
        metadata["total_time_ms"] = int(total_time * 1000)

        # Log slow requests
        if total_time > 3.0:
            logger.warning(
                "slow_rag_request",
                total_time_ms=metadata["total_time_ms"],
                retrieval_time_ms=metadata["retrieval_time_ms"],
                generation_time_ms=metadata["generation_time_ms"],
            )

        logger.info(
            "rag_pipeline_complete",
            total_time_ms=metadata["total_time_ms"],
            chunks_used=len(chunks),
            citations_count=len(citations),
        )

        return response, citations, metadata

    except Exception as e:
        logger.error("rag_pipeline_failed", error=str(e), question_length=len(question))
        raise


async def execute_rag_pipeline_stream(
    question: str,
    conversation_history: List = None,
    selected_text: Optional[str] = None,
    top_k: int = 8,
) -> AsyncGenerator[dict, None]:
    """
    Execute RAG pipeline with streaming response.

    Yields events:
        - {"type": "token", "content": "..."}
        - {"type": "citations", "citations": [...]}
        - {"type": "metadata", "metadata": {...}}
        - {"type": "done"}
    """
    start_time = time.time()
    metadata = {}

    try:
        # Stage 1: Vector Search & Retrieval
        retrieval_start = time.time()

        # Check if user selected text
        if selected_text:
            # Selected text mode: Use selected text as PRIMARY context
            logger.info(
                "selected_text_mode",
                question_length=len(question),
                selected_text_length=len(selected_text),
            )
            print(f"[RAG] Selected text mode - using provided context ({len(selected_text)} chars)")
            print(f"[RAG] Question: '{question}'")

            # Create synthetic chunk from selected text
            chunks = [{
                "chunk_id": "selected_text",
                "text": selected_text,
                "chapter": "Selected Text",
                "section": "User Selection",
                "url": "#",
                "confidence_score": 1.0,  # Maximum confidence for user-selected text
            }]

            # Optionally search for related content to supplement (but don't require it)
            try:
                related_chunks = await search_similar_chunks(
                    query=question,
                    top_k=2,  # Just 2 related chunks to supplement
                    selected_text=None,  # Don't use hybrid search
                )
                if related_chunks:
                    print(f"[RAG] Found {len(related_chunks)} related chunks to supplement")
                    chunks.extend(related_chunks[:2])
                else:
                    print(f"[RAG] No related chunks found - using only selected text")
            except Exception as e:
                print(f"[RAG] Related search failed: {e} - using only selected text")
                # Continue with just selected text

            metadata["chunks_retrieved"] = len(chunks)
            metadata["selected_text_used"] = True

        else:
            # General mode: Vector search only
            chunks = await search_similar_chunks(
                query=question,
                top_k=top_k,
                selected_text=None,
            )

            metadata["chunks_retrieved"] = len(chunks)
            metadata["selected_text_used"] = False

            # Only show error if NO selected text AND no search results
            if not chunks:
                logger.warning("no_chunks_retrieved", question_length=len(question))
                yield {
                    "type": "token",
                    "content": "I couldn't find relevant information in the textbook to answer your question."
                }
                yield {"type": "done"}
                return

        retrieval_time = time.time() - retrieval_start
        metadata["retrieval_time_ms"] = int(retrieval_time * 1000)

        # Stage 2: Build Citations
        citations = build_citations(chunks)
        citations = deduplicate_citations(citations, max_citations=5)

        metadata["avg_confidence"] = round(
            sum(c["confidence_score"] for c in citations) / len(citations),
            2
        ) if citations else 0

        # Stage 3: Build Conversation Context
        formatted_history = []
        if conversation_history:
            formatted_history = build_conversation_history(conversation_history)

        # Stage 4: Stream Response
        generation_start = time.time()
        full_response = ""

        async for token in generate_response_stream(
            question=question,
            chunks=chunks,
            conversation_history=formatted_history,
        ):
            full_response += token
            yield {
                "type": "token",
                "content": token
            }

        generation_time = time.time() - generation_start
        metadata["generation_time_ms"] = int(generation_time * 1000)
        metadata["token_count"] = len(full_response.split())  # Rough estimate

        # Total time
        total_time = time.time() - start_time
        metadata["total_time_ms"] = int(total_time * 1000)

        # Send citations and metadata
        yield {
            "type": "citations",
            "citations": citations
        }

        yield {
            "type": "metadata",
            "metadata": metadata
        }

        yield {"type": "done"}

        logger.info(
            "streaming_rag_complete",
            total_time_ms=metadata["total_time_ms"],
            chunks_used=len(chunks),
        )

    except Exception as e:
        logger.error("streaming_rag_failed", error=str(e))
        yield {
            "type": "error",
            "error": str(e)
        }
