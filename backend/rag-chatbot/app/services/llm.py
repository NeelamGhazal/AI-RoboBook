"""
LLM service for generating responses using OpenAI Agents SDK with OpenRouter.
Includes system prompts and context assembly.
"""
import os
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Tuple
from agents import Agent, Runner
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv

# Load environment variables for LiteLLM
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Ensure OPENROUTER_API_KEY is set as environment variable for LiteLLM
if "OPENROUTER_API_KEY" in os.environ:
    os.environ["OPENROUTER_API_KEY"] = os.environ["OPENROUTER_API_KEY"]

from app.config import settings
from app.utils.logging import get_logger
from app.utils.metrics import GENERATION_DURATION

logger = get_logger(__name__)


# System prompt (static - context will be injected in user message)
SYSTEM_PROMPT = """You are an expert assistant for the "Physical AI & Humanoid Robotics" textbook.

Your task is to answer questions accurately based ONLY on the provided textbook excerpts.

**Guidelines:**
1. Provide clear, accurate answers citing the textbook content
2. If the user selected specific text from the textbook, focus your answer on explaining that selected text
3. When additional related sections are provided, use them to supplement your explanation
4. If the answer is not in the provided excerpts, say "This topic is not covered in the available textbook sections."
5. Do not make up information or use knowledge outside the textbook
6. Be concise but thorough
7. Use technical terminology appropriately

**Selected Text Mode:**
- If the user message includes "USER SELECTED THIS TEXT", they want you to explain that specific text
- Provide a clear, educational explanation of the selected text
- Reference specific parts of the selected text when relevant
- Use any related sections to provide additional context if helpful

Answer the user's question based on the textbook excerpts provided in their message."""

# RAG Agent instance using OpenAI Agents SDK with LiteLLM for OpenRouter
# LiteLLM will automatically use OPENROUTER_API_KEY from environment
RAG_AGENT = Agent(
    name="TextbookRAGAgent",
    model=LitellmModel(
        model="openrouter/nvidia/nemotron-3-super-120b-a12b:free",  # Free OpenRouter model with provider prefix
    ),
    instructions=SYSTEM_PROMPT,
    tools=[],
)


def count_tokens(text: str) -> int:
    """
    Estimate token count for LLM responses.
    Rough approximation based on character count.
    """
    # Rough estimate: 1 token ≈ 4 characters
    return len(text) // 4


def build_context_from_chunks(chunks: List[dict], max_tokens: int = 2000) -> str:
    """
    Build context string from retrieved chunks with token limit.
    Handles selected text mode specially to emphasize user-selected content.

    Args:
        chunks: Retrieved chunks
        max_tokens: Maximum tokens for context

    Returns:
        Formatted context string
    """
    context_parts = []
    current_tokens = 0
    is_selected_text_mode = False

    # Check if first chunk is user-selected text
    if chunks and chunks[0].get("chunk_id") == "selected_text":
        is_selected_text_mode = True
        # Format selected text prominently
        selected_text = chunks[0]["text"]
        chunk_text = f"""**USER SELECTED THIS TEXT FROM THE TEXTBOOK:**

{selected_text}

---"""
        context_parts.append(chunk_text)
        current_tokens += count_tokens(chunk_text)

        # Start supplementary chunks from index 1
        start_index = 1
        if len(chunks) > 1:
            context_parts.append("\n**RELATED TEXTBOOK SECTIONS:**\n")
    else:
        start_index = 0

    # Add remaining chunks
    for i, chunk in enumerate(chunks[start_index:], 1):
        # Format chunk with metadata
        if is_selected_text_mode:
            # Simpler format for supplementary chunks in selected text mode
            chunk_text = f"\n[Additional Source {i}] {chunk['chapter']} - {chunk['section']}\n{chunk['text']}\n"
        else:
            # Standard format for general mode
            chunk_text = f"[Source {i}] Chapter: {chunk['chapter']}, Section: {chunk['section']}\n{chunk['text']}\n"

        chunk_tokens = count_tokens(chunk_text)

        if current_tokens + chunk_tokens > max_tokens:
            logger.debug(
                "context_truncated",
                chunks_used=len(context_parts)-1 if is_selected_text_mode else i-1,
                total_chunks=len(chunks),
                tokens=current_tokens,
            )
            break

        context_parts.append(chunk_text)
        current_tokens += chunk_tokens

    context = "\n".join(context_parts)

    logger.debug(
        "context_built",
        chunks_used=len(context_parts),
        estimated_tokens=current_tokens,
        selected_text_mode=is_selected_text_mode,
    )

    return context


def build_conversation_history(messages: List[dict], max_messages: int = 12) -> List[dict]:
    """
    Build conversation history for context.

    Args:
        messages: Recent messages from DB
        max_messages: Maximum messages to include

    Returns:
        Formatted messages for Agents SDK
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
    Generate response using OpenAI Agents SDK with OpenRouter (non-streaming).

    Args:
        question: User's question
        chunks: Retrieved chunks
        conversation_history: Previous conversation messages
        temperature: Sampling temperature (not used with Agents SDK)

    Returns:
        Tuple of (response_text, token_count)
    """
    with GENERATION_DURATION.time():
        try:
            # Build context from chunks
            context = build_context_from_chunks(chunks)

            # Inject context into user message
            user_message_with_context = f"""**Textbook Excerpts:**

{context}

**Question:** {question}"""

            # Build messages array for Agents SDK
            messages = []

            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)

            # Add current question with embedded context
            messages.append({
                "role": "user",
                "content": user_message_with_context
            })

            # Generate response using Agents SDK Runner (non-streaming)
            result = await Runner.run(RAG_AGENT, messages)
            response = result.final_output

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
    Generate streaming response using OpenAI Agents SDK with OpenRouter.

    Args:
        question: User's question
        chunks: Retrieved chunks
        conversation_history: Previous conversation messages
        temperature: Sampling temperature (not used with Agents SDK)

    Yields:
        Response tokens as they are generated
    """
    try:
        # Build context from chunks
        context = build_context_from_chunks(chunks)

        # Inject context into user message (T013: new pattern)
        user_message_with_context = f"""**Textbook Excerpts:**

{context}

**Question:** {question}"""

        # Build messages array for Agents SDK
        messages = []

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)

        # Add current question with embedded context
        messages.append({
            "role": "user",
            "content": user_message_with_context
        })

        # Log agent request started
        logger.info(
            "agent_request_started",
            question_length=len(question),
            chunks_used=len(chunks),
            history_messages=len(conversation_history) if conversation_history else 0,
        )

        # Stream response using Agents SDK Runner (T012, T014)
        full_response = ""
        run_result = Runner.run_streamed(RAG_AGENT, messages)

        event_count = 0
        async for event in run_result.stream_events():
            event_count += 1

            # Handle raw_response_event from LiteLLM/OpenAI Agents SDK
            if event.type == "raw_response_event" and hasattr(event, "data"):
                chunk = event.data

                # Extract response from ResponseCreatedEvent
                if hasattr(chunk, "response") and chunk.response:
                    response_obj = chunk.response

                    # OpenAI Agents SDK Response object contains the output
                    if hasattr(response_obj, "output") and response_obj.output:
                        output_content = response_obj.output

                        # Output is a list of ResponseOutputMessage objects
                        if isinstance(output_content, list):
                            for content_block in output_content:
                                # ResponseOutputMessage has a 'content' field with text blocks
                                if hasattr(content_block, "content"):
                                    content_field = content_block.content

                                    # Content is a list of ResponseOutputText objects
                                    if isinstance(content_field, list):
                                        for text_block in content_field:
                                            # Extract text from ResponseOutputText
                                            if hasattr(text_block, "text"):
                                                text = text_block.text
                                                full_response += text
                                                yield text
                                    # Content is a string
                                    elif isinstance(content_field, str):
                                        full_response += content_field
                                        yield content_field

                                # Direct text field (fallback)
                                elif hasattr(content_block, "text"):
                                    text = content_block.text
                                    full_response += text
                                    yield text

                        # Output is a single string (fallback)
                        elif isinstance(output_content, str):
                            full_response += output_content
                            yield output_content

            # Handle content delta events (original expected type)
            elif event.type == "content_delta":
                token = event.delta
                full_response += token
                yield token

            # Handle error events
            elif event.type == "error":
                error_msg = getattr(event, "error", "Unknown error")
                logger.error("agent_error", error=str(error_msg))
                raise RuntimeError(f"Agent SDK error: {error_msg}")

        # Log completion
        token_count = count_tokens(full_response)
        logger.info(
            "agent_response_complete",
            response_length=len(full_response),
            token_count=token_count,
            chunks_used=len(chunks),
        )

    except Exception as e:
        logger.error("streaming_generation_failed", error=str(e))
        raise
