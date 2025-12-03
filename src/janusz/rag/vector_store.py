#!/usr/bin/env python3
"""
Vector Store Interface for RAG System

Provides unified interface for different vector databases (FAISS, ChromaDB, etc.)
with automatic fallback and chunking support.
"""

import logging
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models import VectorDocument

logger = logging.getLogger(__name__)


class VectorStoreError(Exception):
    """Exception raised when vector store operations fail."""
    pass


class VectorStoreBase(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    def add_documents(self, documents: List[VectorDocument]) -> List[str]:
        """Add documents to the vector store. Returns document IDs."""
        pass

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar documents. Returns (doc_id, score) pairs."""
        pass

    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the store."""
        pass

    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Retrieve a document by ID."""
        pass

    @abstractmethod
    def list_documents(self, limit: int = 100) -> List[str]:
        """List all document IDs in the store."""
        pass

    @abstractmethod
    def clear(self):
        """Clear all documents from the store."""
        pass


class FAISSVectorStore(VectorStoreBase):
    """FAISS-based vector store for local, fast semantic search."""

    def __init__(self, dimension: int = 1536, index_file: Optional[str] = None):
        """
        Initialize FAISS vector store.

        Args:
            dimension: Embedding dimension (1536 for OpenAI ada-002)
            index_file: Optional file path to save/load index
        """
        try:
            import faiss
        except ImportError as err:
            raise VectorStoreError("FAISS not available. Install with: pip install faiss-cpu") from err

        self.dimension = dimension
        self._faiss = faiss  # Store faiss reference
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.doc_store: Dict[str, VectorDocument] = {}
        self.index_file = Path(index_file) if index_file else None

        # Load existing index if available
        if self.index_file and self.index_file.exists():
            self._load_index()

    def add_documents(self, documents: List[VectorDocument]) -> List[str]:
        """Add documents with embeddings to FAISS index."""
        if not documents:
            return []

        doc_ids = []
        embeddings = []

        for doc in documents:
            if doc.embedding is None:
                logger.warning(f"Document {doc.id} has no embedding, skipping")
                continue

            # Generate unique ID if not provided
            if not doc.id:
                doc.id = str(uuid.uuid4())

            self.doc_store[doc.id] = doc
            doc_ids.append(doc.id)
            embeddings.append(doc.embedding)

        if embeddings:
            import numpy as np
            embeddings_array = np.array(embeddings, dtype=np.float32)
            self.index.add(embeddings_array)
            logger.info(f"Added {len(embeddings)} documents to FAISS index")

            # Save index if configured
            if self.index_file:
                self._save_index()

        return doc_ids

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search for similar documents using FAISS."""
        if self.index.ntotal == 0:
            return []

        import numpy as np
        query_array = np.array([query_embedding], dtype=np.float32)

        try:
            scores, indices = self.index.search(query_array, min(top_k, self.index.ntotal))

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.doc_store):  # Safety check
                    doc_ids = list(self.doc_store.keys())
                    doc_id = doc_ids[idx]
                    results.append((doc_id, float(score)))

            return results

        except Exception as e:
            logger.error(f"FAISS search failed: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete document from FAISS (requires full rebuild)."""
        if doc_id not in self.doc_store:
            return False

        # FAISS doesn't support deletion, so we need to rebuild the index
        del self.doc_store[doc_id]
        self._rebuild_index()
        return True

    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Get document by ID."""
        return self.doc_store.get(doc_id)

    def list_documents(self, limit: int = 100) -> List[str]:
        """List document IDs."""
        return list(self.doc_store.keys())[:limit]

    def clear(self):
        """Clear all documents."""
        self.doc_store.clear()
        self.index.reset()
        if self.index_file and self.index_file.exists():
            self.index_file.unlink()

    def _rebuild_index(self):
        """Rebuild FAISS index after document deletion."""
        if not self.doc_store:
            self.index.reset()
            return

        import numpy as np
        embeddings = [doc.embedding for doc in self.doc_store.values() if doc.embedding]

        if embeddings:
            embeddings_array = np.array(embeddings, dtype=np.float32)
            self.index = type(self.index)(self.dimension)  # Create new index
            self.index.add(embeddings_array)

        if self.index_file:
            self._save_index()

    def _save_index(self):
        """Save FAISS index to file."""
        try:
            self._faiss.write_index(self.index, str(self.index_file))
            logger.info(f"Saved FAISS index to {self.index_file}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {e}")

    def _load_index(self):
        """Load FAISS index from file."""
        try:
            self.index = self._faiss.read_index(str(self.index_file))
            logger.info(f"Loaded FAISS index from {self.index_file}")
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            self.index = type(self.index)(self.dimension)


class ChromaDBVectorStore(VectorStoreBase):
    """ChromaDB-based vector store for persistent semantic search."""

    def __init__(self, collection_name: str = "janusz_docs", persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB vector store.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist the database
        """
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError as err:
            raise VectorStoreError("ChromaDB not available. Install with: pip install chromadb") from err

        self.collection_name = collection_name
        self.persist_directory = persist_directory

        # Initialize ChromaDB client
        settings = Settings()
        if persist_directory:
            settings.persist_directory = persist_directory
            settings.is_persistent = True

        self.client = chromadb.PersistentClient(path=persist_directory) if persist_directory else chromadb.Client()
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, documents: List[VectorDocument]) -> List[str]:
        """Add documents to ChromaDB collection."""
        if not documents:
            return []

        ids = []
        embeddings = []
        metadatas = []
        documents_text = []

        for doc in documents:
            if doc.embedding is None:
                logger.warning(f"Document {doc.id} has no embedding, skipping")
                continue

            # Generate unique ID if not provided
            doc_id = doc.id or str(uuid.uuid4())

            ids.append(doc_id)
            embeddings.append(doc.embedding)
            metadatas.append(doc.metadata or {})
            documents_text.append(doc.content)

            # Store full document for retrieval
            doc.id = doc_id

        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text
            )
            logger.info(f"Added {len(ids)} documents to ChromaDB")

        return ids

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        """Search ChromaDB collection."""
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["distances"]
            )

            search_results = []
            if results['ids'] and results['distances']:
                for doc_id, distance in zip(results['ids'][0], results['distances'][0]):
                    # Convert distance to similarity score (ChromaDB returns distances)
                    score = 1.0 / (1.0 + distance)  # Simple conversion
                    search_results.append((doc_id, score))

            return search_results

        except Exception as e:
            logger.error(f"ChromaDB search failed: {e}")
            return []

    def delete_document(self, doc_id: str) -> bool:
        """Delete document from ChromaDB."""
        try:
            self.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    def get_document(self, doc_id: str) -> Optional[VectorDocument]:
        """Get document by ID from ChromaDB."""
        try:
            result = self.collection.get(ids=[doc_id], include=["embeddings", "metadatas", "documents"])
            if result['ids']:
                return VectorDocument(
                    id=doc_id,
                    content=result['documents'][0] if result['documents'] else "",
                    metadata=result['metadatas'][0] if result['metadatas'] else {},
                    embedding=result['embeddings'][0] if result['embeddings'] else None
                )
        except Exception as e:
            logger.error(f"Failed to get document {doc_id}: {e}")

        return None

    def list_documents(self, limit: int = 100) -> List[str]:
        """List document IDs in ChromaDB."""
        try:
            result = self.collection.get(limit=limit, include=[])
            return result['ids']
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []

    def clear(self):
        """Clear ChromaDB collection."""
        try:
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(name=self.collection_name)
            logger.info("Cleared ChromaDB collection")
        except Exception as e:
            logger.error(f"Failed to clear ChromaDB collection: {e}")


class VectorStoreFactory:
    """Factory for creating vector stores with automatic fallback."""

    @staticmethod
    def create_vector_store(store_type: str = "auto", **kwargs) -> VectorStoreBase:
        """
        Create a vector store with automatic fallback.

        Args:
            store_type: Type of store ("faiss", "chromadb", "auto")
            **kwargs: Store-specific arguments

        Returns:
            Vector store instance
        """
        if store_type == "faiss" or (store_type == "auto" and VectorStoreFactory._is_faiss_available()):
            try:
                return FAISSVectorStore(**kwargs)
            except VectorStoreError:
                if store_type == "faiss":
                    raise

        if store_type == "chromadb" or (store_type == "auto" and VectorStoreFactory._is_chromadb_available()):
            try:
                return ChromaDBVectorStore(**kwargs)
            except VectorStoreError:
                if store_type == "chromadb":
                    raise

        # Fallback to simple in-memory store (not implemented yet)
        raise VectorStoreError("No vector store available. Install FAISS or ChromaDB.")

    @staticmethod
    def _is_faiss_available() -> bool:
        """Check if FAISS is available."""
        import importlib.util
        return importlib.util.find_spec("faiss") is not None

    @staticmethod
    def _is_chromadb_available() -> bool:
        """Check if ChromaDB is available."""
        import importlib.util
        return importlib.util.find_spec("chromadb") is not None
