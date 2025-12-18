"""
Local embedding client using sentence-transformers.
Completely free, no API key needed, unlimited usage.
Uses all-MiniLM-L6-v2 model (384 dimensions).
"""
import asyncio
from typing import List, Optional
import numpy as np

from sentence_transformers import SentenceTransformer

from app.utils.logging import get_logger

logger = get_logger(__name__)


class LocalEmbeddingClient:
    """Local embedding client using sentence-transformers (no API needed)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent embedding tasks

    async def initialize(self) -> None:
        """Initialize the sentence-transformers model."""
        try:
            # Load model (downloads on first run, cached afterwards)
            logger.info("Loading local embedding model...", model=self.model_name)
            self.model = await asyncio.to_thread(
                SentenceTransformer, self.model_name
            )
            logger.info(
                "local_embedding_model_loaded",
                model=self.model_name,
                embedding_dim=self.model.get_sentence_embedding_dimension(),
            )
        except Exception as e:
            logger.error("local_embedding_model_load_failed", error=str(e))
            raise

    async def close(self) -> None:
        """Close the client (cleanup if needed)."""
        logger.info("local_embedding_client_closed")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using local model.

        Args:
            text: Text to embed

        Returns:
            384-dimensional embedding vector
        """
        async with self.semaphore:
            try:
                # Generate embedding using sentence-transformers
                embedding = await asyncio.to_thread(
                    self.model.encode,
                    text,
                    convert_to_numpy=True,
                    normalize_embeddings=True,  # L2 normalization for cosine similarity
                )

                # Convert numpy array to list
                embedding_list = embedding.tolist()

                logger.debug(
                    "embedding_generated",
                    text_length=len(text),
                    dimensions=len(embedding_list),
                )
                return embedding_list

            except Exception as e:
                logger.error("embedding_generation_failed", error=str(e), text_length=len(text))
                raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch (more efficient).

        Args:
            texts: List of texts to embed

        Returns:
            List of 384-dimensional embedding vectors
        """
        async with self.semaphore:
            try:
                # Batch encode for efficiency
                embeddings_np = await asyncio.to_thread(
                    self.model.encode,
                    texts,
                    convert_to_numpy=True,
                    normalize_embeddings=True,  # L2 normalization
                    show_progress_bar=len(texts) > 100,  # Show progress for large batches
                )

                # Convert numpy array to list of lists
                embeddings = embeddings_np.tolist()

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


# Global local embedding client instance
local_embedding_client = LocalEmbeddingClient()
