"""
LLM service for generating responses using Google Gemini 1.5 Flash.
Includes system prompts and context assembly.
Free tier compatible - no cost for embeddings or generation.
"""
from typing import AsyncGenerator, List, Optional, Tuple

from app.clients.gemini_client import gemini_client
from app.utils.logging import get_logger
from app.utils.metrics import GENERATION_DURATION

logger = get_logger(__name__)


# System prompt template
SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

Your task is to answer questions accurately based ONLY on the provided textbook excerpts below.

**Guidelines:**
1. Provide clear, accurate answers citing the textbook content
2. If the answer is not in the provided excerpts, say "This topic is not covered in the available textbook sections."
3. Do not make up information or use knowledge outside the textbook
4. Be concise but thorough
5. Use technical terminology appropriately

**Textbook Excerpts:**

{context}

Answer the user's question based on these excerpts."""


def count_tokens(text: str) -> int:
    """
    Estimate token count for Gemini models.
    Gemini uses a similar tokenizer to GPT, so we use a rough estimate.
    """
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4


def build_context_from_chunks(chunks: List[dict], max_tokens: int = 2000) -> str:
    """
    Build context string from retrieved chunks with token limit.

    Args:
        chunks: Retrieved chunks
        max_tokens: Maximum tokens for context

    Returns:
        Formatted context string
    """
    context_parts = []
    current_tokens = 0

    for i, chunk in enumerate(chunks, 1):
        # Format chunk with metadata
        chunk_text = f"[Source {i}] Chapter: {chunk['chapter']}, Section: {chunk['section']}\n{chunk['text']}\n"

        chunk_tokens = count_tokens(chunk_text)

        if current_tokens + chunk_tokens > max_tokens:
            logger.debug(
                "context_truncated",
                chunks_used=i-1,
                total_chunks=len(chunks),
                tokens=current_tokens,
            )
            break

        context_parts.append(chunk_text)
        current_tokens += chunk_tokens

    context = "\n---\n".join(context_parts)

    logger.debug(
        "context_built",
        chunks_used=len(context_parts),
        estimated_tokens=current_tokens,
    )

    return context


def build_conversation_history(messages: List[dict], max_messages: int = 12) -> List[dict]:
    """
    Build conversation history for context.

    Args:
        messages: Recent messages from DB
        max_messages: Maximum messages to include

    Returns:
        Formatted messages for Gemini API
    """
    # Take most recent messages (already reversed in CRUD)
    recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

    formatted = []
    for msg in recent_messages:
        formatted.append({
            "role": msg.role,
            "content": msg.content,
        })

    logger.debug("conversation_history_built", message_count=len(formatted))

    return formatted


async def generate_response(
    question: str,
    chunks: List[dict],
    conversation_history: List[dict] = None,
    temperature: float = 0.7,
) -> Tuple[str, int]:
    """
    Generate response using Gemini 1.5 Flash (non-streaming).

    Args:
        question: User's question
        chunks: Retrieved chunks
        conversation_history: Previous conversation messages
        temperature: Sampling temperature

    Returns:
        Tuple of (response_text, token_count)
    """
    with GENERATION_DURATION.time():
        try:
            # Build context from chunks
            context = build_context_from_chunks(chunks)

            # Build system prompt with context
            system_prompt = SYSTEM_PROMPT.format(context=context)

            # Build messages array
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current question
            messages.append({
                "role": "user",
                "content": question
            })

            # Generate response using Gemini
            response = await gemini_client.generate_chat_completion(
                messages=messages,
                temperature=temperature,
            )

            # Count tokens (rough estimate)
            token_count = count_tokens(response)

            logger.info(
                "response_generated",
                response_length=len(response),
                token_count=token_count,
                chunks_used=len(chunks),
            )

            return response, token_count

        except Exception as e:
            logger.error("response_generation_failed", error=str(e))
            raise


async def generate_response_stream(
    question: str,
    chunks: List[dict],
    conversation_history: List[dict] = None,
    temperature: float = 0.7,
) -> AsyncGenerator[str, None]:
    """
    Generate streaming response using Gemini 1.5 Flash.

    Args:
        question: User's question
        chunks: Retrieved chunks
        conversation_history: Previous conversation messages
        temperature: Sampling temperature

    Yields:
        Response tokens as they are generated
    """
    try:
        # Build context from chunks
        context = build_context_from_chunks(chunks)

        # Build system prompt with context
        system_prompt = SYSTEM_PROMPT.format(context=context)

        # Build messages array
        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current question
        messages.append({
            "role": "user",
            "content": question
        })

        # Stream response using Gemini
        full_response = ""
        async for token in gemini_client.generate_chat_completion_stream(
            messages=messages,
            temperature=temperature,
        ):
            full_response += token
            yield token

        # Log completion
        token_count = count_tokens(full_response)
        logger.info(
            "streaming_response_complete",
            response_length=len(full_response),
            token_count=token_count,
            chunks_used=len(chunks),
        )

    except Exception as e:
        logger.error("streaming_generation_failed", error=str(e))
        raise
