#!/usr/bin/env python3
"""
Embedding System for RAG

Provides text-to-vector conversion using various embedding models
with automatic fallback and chunking support.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    """Configuration for embedding models."""
    model_name: str = "text-embedding-ada-002"
    dimension: int = 1536
    max_tokens: int = 8191
    chunk_size: int = 1000
    chunk_overlap: int = 200


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Convert text to embedding vector."""
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to embedding vectors."""
        pass

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Return embedding dimension."""
        pass

    @property
    @abstractmethod
    def max_tokens(self) -> int:
        """Return maximum tokens per request."""
        pass


class OpenRouterEmbeddings(EmbeddingProvider):
    """OpenRouter-based embeddings using various models."""

    def __init__(self, model: str = "text-embedding-ada-002", api_key: Optional[str] = None):
        """
        Initialize OpenRouter embeddings.

        Args:
            model: Embedding model to use
            api_key: OpenRouter API key
        """
        self.api_key = api_key or os.getenv("JANUSZ_OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key not provided")

        self.model = model
        self._dimension = self._get_model_dimension(model)
        self._max_tokens = 8191  # Conservative limit

        try:
            import httpx
            self.client = httpx.Client(
                base_url="https://openrouter.ai/api/v1",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/your-username/janusz",
                    "X-Title": "Janusz AI Document Processor"
                },
                timeout=30.0
            )
        except ImportError as err:
            raise ImportError("httpx required for OpenRouter embeddings") from err

    def embed_text(self, text: str) -> List[float]:
        """Convert single text to embedding."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to embeddings."""
        # Simple implementation - could be optimized with batching
        embeddings = []

        for text in texts:
            if not text.strip():
                # Return zero vector for empty text
                embeddings.append([0.0] * self.dimension)
                continue

            # Truncate if too long
            truncated_text = text[:self.max_tokens]

            try:
                response = self.client.post("/embeddings", json={
                    "model": self.model,
                    "input": truncated_text
                })

                response.raise_for_status()
                data = response.json()

                if "data" in data and data["data"]:
                    embedding = data["data"][0]["embedding"]
                    embeddings.append(embedding)
                else:
                    logger.warning("No embedding data in response")
                    embeddings.append([0.0] * self.dimension)

            except Exception as e:
                logger.error(f"Embedding failed for text: {e}")
                embeddings.append([0.0] * self.dimension)

        return embeddings

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    @property
    def max_tokens(self) -> int:
        """Return maximum tokens per request."""
        return self._max_tokens

    def _get_model_dimension(self, model: str) -> int:
        """Get embedding dimension for model."""
        # Known dimensions for common models
        dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-similarity-ada-001": 1024,
        }
        return dimensions.get(model, 1536)  # Default to 1536


class SentenceTransformerEmbeddings(EmbeddingProvider):
    """Local sentence transformer embeddings as fallback."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize sentence transformer embeddings.

        Args:
            model_name: HuggingFace model name
        """
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as err:
            raise ImportError("sentence-transformers required for local embeddings") from err

        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
        self._max_tokens = 512  # Conservative limit for local models

    def embed_text(self, text: str) -> List[float]:
        """Convert text to embedding using sentence transformer."""
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Convert multiple texts to embeddings."""
        try:
            embeddings = self.model.encode(texts, convert_to_list=True)
            return embeddings
        except Exception as e:
            logger.error(f"Sentence transformer embedding failed: {e}")
            # Return zero vectors as fallback
            return [[0.0] * self.dimension for _ in texts]

    @property
    def dimension(self) -> int:
        """Return embedding dimension."""
        return self._dimension

    @property
    def max_tokens(self) -> int:
        """Return maximum tokens per request."""
        return self._max_tokens


class TextChunker:
    """Utility for chunking long texts for embedding."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize text chunker.

        Args:
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk

        Returns:
            List of chunk dictionaries with text and metadata
        """
        if len(text) <= self.chunk_size:
            return [{
                "text": text,
                "start": 0,
                "end": len(text),
                "chunk_id": 0
            }]

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # If not at the end, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings in the last 100 chars
                search_start = max(end - 100, start + self.chunk_size // 2)
                sentence_end = self._find_sentence_end(text, search_start, end)

                if sentence_end:
                    end = sentence_end

            chunk_text = text[start:end]
            chunks.append({
                "text": chunk_text,
                "start": start,
                "end": end,
                "chunk_id": chunk_id
            })

            # Move start position with overlap
            start = end - self.overlap
            chunk_id += 1

        return chunks

    def _find_sentence_end(self, text: str, start: int, end: int) -> Optional[int]:
        """Find sentence ending within the specified range."""
        sentence_markers = ['. ', '! ', '? ', '\n\n']

        for marker in sentence_markers:
            pos = text.rfind(marker, start, end)
            if pos != -1:
                return pos + len(marker)

        return None


class EmbeddingManager:
    """Manager for embedding operations with automatic fallback."""

    def __init__(self, config: Optional[EmbeddingConfig] = None):
        """
        Initialize embedding manager.

        Args:
            config: Embedding configuration
        """
        self.config = config or EmbeddingConfig()
        self.chunker = TextChunker(self.config.chunk_size, self.config.chunk_overlap)
        self._embedding_provider = None

    @property
    def embedding_provider(self) -> EmbeddingProvider:
        """Get or create embedding provider with fallback."""
        if self._embedding_provider is None:
            self._embedding_provider = self._create_embedding_provider()
        return self._embedding_provider

    def embed_text(self, text: str) -> List[float]:
        """Embed single text."""
        return self.embedding_provider.embed_text(text)

    def embed_document(self, content: str, chunk: bool = True) -> Dict[str, Any]:
        """
        Embed document content, optionally with chunking.

        Args:
            content: Document content
            chunk: Whether to chunk long documents

        Returns:
            Dictionary with embeddings and chunk information
        """
        if chunk and len(content) > self.config.chunk_size:
            # Chunk the document
            chunks = self.chunker.chunk_text(content)

            # Embed each chunk
            chunk_embeddings = []
            for chunk in chunks:
                embedding = self.embed_text(chunk["text"])
                chunk_embeddings.append({
                    **chunk,
                    "embedding": embedding
                })

            # Create overall document embedding (average of chunks)
            all_embeddings = [ce["embedding"] for ce in chunk_embeddings]
            doc_embedding = self._average_embeddings(all_embeddings)

            return {
                "document_embedding": doc_embedding,
                "chunks": chunk_embeddings,
                "chunked": True
            }
        else:
            # Embed as single piece
            embedding = self.embed_text(content)
            return {
                "document_embedding": embedding,
                "chunks": [{
                    "text": content,
                    "start": 0,
                    "end": len(content),
                    "chunk_id": 0,
                    "embedding": embedding
                }],
                "chunked": False
            }

    def _create_embedding_provider(self) -> EmbeddingProvider:
        """Create embedding provider with automatic fallback."""
        # Try OpenRouter first
        try:
            return OpenRouterEmbeddings(self.config.model_name)
        except (ValueError, ImportError):
            logger.info("OpenRouter embeddings not available, trying local models")

        # Fallback to sentence transformers
        try:
            return SentenceTransformerEmbeddings()
        except ImportError:
            logger.warning("No embedding providers available")

        # Last resort - dummy provider
        return DummyEmbeddings()

    def _average_embeddings(self, embeddings: List[List[float]]) -> List[float]:
        """Average multiple embeddings."""
        if not embeddings:
            return [0.0] * self.embedding_provider.dimension

        import numpy as np
        embeddings_array = np.array(embeddings)
        averaged = np.mean(embeddings_array, axis=0)
        return averaged.tolist()


class DummyEmbeddings(EmbeddingProvider):
    """Dummy embedding provider for testing when no real providers are available."""

    def __init__(self, dimension: int = 384):
        self._dimension = dimension

    def embed_text(self, text: str) -> List[float]:
        """Return zero vector for dummy embeddings."""
        return [0.0] * self.dimension

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Return zero vectors for batch."""
        return [[0.0] * self.dimension for _ in texts]

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def max_tokens(self) -> int:
        return 10000  # Unlimited for dummy


# Import here to avoid circular imports
import os  # noqa: E402
