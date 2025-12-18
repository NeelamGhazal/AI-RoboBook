"""
Google Gemini client wrapper with connection pooling and rate limiting.
Uses google-generativeai SDK for embeddings and text generation.
Fully compatible with free tier (no cost).
"""
import asyncio
from typing import Any, AsyncGenerator, List, Optional

import google.generativeai as genai
from google.generativeai.types import GenerateContentResponse

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class GeminiClient:
    """Async Gemini client with connection pooling and concurrency limiting."""

    def __init__(self):
        self.embedding_model: Optional[Any] = None
        self.generation_model: Optional[Any] = None
        self.semaphore = asyncio.Semaphore(10)  # Max 10 concurrent Gemini calls

    async def initialize(self) -> None:
        """Initialize Gemini client with API key."""
        try:
            # Configure API key
            genai.configure(api_key=settings.GOOGLE_API_KEY)

            # Initialize embedding model (models/embedding-001 - 768 dimensions, free)
            self.embedding_model = genai.GenerativeModel(settings.GEMINI_EMBEDDING_MODEL)

            # Initialize generation model (gemini-1.5-flash - fast and free)
            self.generation_model = genai.GenerativeModel(
                model_name=settings.GEMINI_MODEL,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )

            logger.info(
                "gemini_client_initialized",
                embedding_model=settings.GEMINI_EMBEDDING_MODEL,
                generation_model=settings.GEMINI_MODEL
            )
        except Exception as e:
            logger.error("gemini_client_init_failed", error=str(e))
            raise

    async def close(self) -> None:
        """Close Gemini client (cleanup if needed)."""
        logger.info("gemini_client_closed")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using Gemini embedding model.
        Returns 768-dimensional vector (models/embedding-001).
        """
        async with self.semaphore:
            try:
                # Gemini embedding API is synchronous but we wrap for async consistency
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model=settings.GEMINI_EMBEDDING_MODEL,
                    content=text,
                    task_type="retrieval_document"
                )

                embedding = result['embedding']

                logger.debug(
                    "embedding_generated",
                    text_length=len(text),
                    dimensions=len(embedding),
                )
                return embedding

            except Exception as e:
                logger.error("embedding_generation_failed", error=str(e), text_length=len(text))
                raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.
        More efficient for ingestion pipeline.
        """
        async with self.semaphore:
            try:
                # Gemini supports batch embedding
                embeddings = []

                # Process in chunks of 100 (Gemini API limit)
                chunk_size = 100
                for i in range(0, len(texts), chunk_size):
                    chunk = texts[i:i + chunk_size]

                    # Batch embed
                    results = await asyncio.to_thread(
                        lambda: [
                            genai.embed_content(
                                model=settings.GEMINI_EMBEDDING_MODEL,
                                content=text,
                                task_type="retrieval_document"
                            )['embedding']
                            for text in chunk
                        ]
                    )

                    embeddings.extend(results)

                logger.info(
                    "batch_embeddings_generated",
                    batch_size=len(texts),
                    dimensions=len(embeddings[0]) if embeddings else 0,
                )
                return embeddings

            except Exception as e:
                logger.error(
                    "batch_embedding_failed", error=str(e), batch_size=len(texts)
                )
                raise

    async def generate_chat_completion(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate chat completion (non-streaming).
        Used for basic Q&A without streaming.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response
        """
        async with self.semaphore:
            try:
                # Convert OpenAI-style messages to Gemini format
                prompt = self._convert_messages_to_prompt(messages)

                # Generate response
                response = await asyncio.to_thread(
                    self.generation_model.generate_content,
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens or 2048,
                    }
                )

                content = response.text

                logger.debug(
                    "chat_completion_generated",
                    model=settings.GEMINI_MODEL,
                    response_length=len(content),
                )
                return content

            except Exception as e:
                logger.error("chat_completion_failed", error=str(e))
                raise

    async def generate_chat_completion_stream(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming chat completion.
        Yields tokens as they are generated.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they are generated
        """
        async with self.semaphore:
            try:
                # Convert OpenAI-style messages to Gemini format
                prompt = self._convert_messages_to_prompt(messages)

                # Generate streaming response
                response = await asyncio.to_thread(
                    self.generation_model.generate_content,
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens or 2048,
                    },
                    stream=True
                )

                # Stream chunks
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

                logger.debug("streaming_completion_finished", model=settings.GEMINI_MODEL)

            except Exception as e:
                logger.error("streaming_completion_failed", error=str(e))
                raise

    def _convert_messages_to_prompt(self, messages: List[dict]) -> str:
        """
        Convert OpenAI-style messages to Gemini prompt format.

        Gemini uses a simpler prompt structure:
        - System message becomes part of the prompt
        - User/assistant messages are concatenated

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Formatted prompt string
        """
        prompt_parts = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                # System message goes first
                prompt_parts.insert(0, content)
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")

        return "\n\n".join(prompt_parts)


# Global Gemini client instance
gemini_client = GeminiClient()
