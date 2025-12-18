"""
OpenAI client wrapper with connection pooling and rate limiting.
Uses httpx for async operations with semaphore for concurrency control.
"""
import asyncio
from typing import Any, AsyncGenerator, List, Optional

import httpx
from openai import AsyncOpenAI

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """Async OpenAI client with connection pooling and concurrency limiting."""

    def __init__(self):
        self.client: Optional[AsyncOpenAI] = None
        self.semaphore = asyncio.Semaphore(10)  # Max 10 concurrent OpenAI calls

    async def initialize(self) -> None:
        """Initialize OpenAI client."""
        try:
            self.client = AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                timeout=httpx.Timeout(30.0, connect=5.0),
                max_retries=3,
            )
            logger.info("openai_client_initialized")
        except Exception as e:
            logger.error("openai_client_init_failed", error=str(e))
            raise

    async def close(self) -> None:
        """Close OpenAI client."""
        if self.client:
            await self.client.close()
            logger.info("openai_client_closed")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using text-embedding-3-small.
        Returns 1536-dimensional vector.
        """
        async with self.semaphore:
            try:
                response = await self.client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL, input=text
                )
                embedding = response.data[0].embedding
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
                response = await self.client.embeddings.create(
                    model=settings.OPENAI_EMBEDDING_MODEL, input=texts
                )
                embeddings = [item.embedding for item in response.data]
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
        """
        async with self.semaphore:
            try:
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = response.choices[0].message.content
                logger.debug(
                    "chat_completion_generated",
                    model=settings.OPENAI_MODEL,
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
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
        """
        async with self.semaphore:
            try:
                stream = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )

                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

                logger.debug("streaming_completion_finished", model=settings.OPENAI_MODEL)

            except Exception as e:
                logger.error("streaming_completion_failed", error=str(e))
                raise


# Global OpenAI client instance
openai_client = OpenAIClient()
