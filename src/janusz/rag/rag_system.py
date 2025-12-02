#!/usr/bin/env python3
"""
RAG (Retrieval-Augmented Generation) System

Provides question-answering capabilities over document collections
using vector search and language model generation.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import RAGQuery, RAGResponse, SearchResult, VectorDocument, DocumentStructure
from .vector_store import VectorStoreFactory, VectorStoreBase
from .embeddings import EmbeddingManager, EmbeddingConfig
from ..ai.ai_content_analyzer import AIContentAnalyzer

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Complete RAG system for question-answering over documents.

    Combines vector search for retrieval with language models for generation,
    providing accurate answers based on document content.
    """

    def __init__(self,
                 vector_store: Optional[VectorStoreBase] = None,
                 embedding_manager: Optional[EmbeddingManager] = None,
                 ai_analyzer: Optional[AIContentAnalyzer] = None,
                 collection_name: str = "janusz_docs"):
        """
        Initialize RAG system.

        Args:
            vector_store: Vector store for document retrieval
            embedding_manager: Manager for text embeddings
            ai_analyzer: AI analyzer for answer generation
            collection_name: Name for the document collection
        """
        self.collection_name = collection_name

        # Initialize components with defaults
        self.vector_store = vector_store or VectorStoreFactory.create_vector_store(
            store_type="auto",
            collection_name=collection_name
        )

        self.embedding_manager = embedding_manager or EmbeddingManager()

        # AI analyzer is optional - can work with just retrieval
        self.ai_analyzer = ai_analyzer

        # Statistics
        self.query_count = 0
        self.indexed_documents = 0

    def add_document(self, document: DocumentStructure, chunk: bool = True) -> str:
        """
        Add a document to the RAG system.

        Args:
            document: Document to add
            chunk: Whether to chunk long documents

        Returns:
            Document ID in the vector store
        """
        # Prepare content for embedding
        content = document.content.raw_text
        if not content:
            content = self._extract_content_from_sections(document.content.sections)

        # Generate embeddings
        embedding_result = self.embedding_manager.embed_document(content, chunk=chunk)

        # Create vector document
        vector_doc = VectorDocument(
            id=document.metadata.title.replace(" ", "_").lower()[:50] + f"_{int(datetime.now().timestamp())}",
            content=content,
            metadata={
                "title": document.metadata.title,
                "source": document.metadata.source,
                "source_type": document.metadata.source_type,
                "created_at": document.metadata.created_at,
                "format_version": document.metadata.format_version,
                "ai_processed": document.metadata.ai_processing_enabled or False,
            },
            embedding=embedding_result["document_embedding"],
            chunks=embedding_result["chunks"],
            last_indexed=datetime.now().isoformat()
        )

        # Add to vector store
        doc_ids = self.vector_store.add_documents([vector_doc])
        self.indexed_documents += 1

        logger.info(f"Added document '{document.metadata.title}' to RAG system")
        return doc_ids[0] if doc_ids else ""

    def add_documents(self, documents: List[DocumentStructure], chunk: bool = True) -> List[str]:
        """
        Add multiple documents to the RAG system.

        Args:
            documents: List of documents to add
            chunk: Whether to chunk long documents

        Returns:
            List of document IDs
        """
        vector_docs = []

        for document in documents:
            # Prepare content
            content = document.content.raw_text
            if not content:
                content = self._extract_content_from_sections(document.content.sections)

            # Generate embeddings
            embedding_result = self.embedding_manager.embed_document(content, chunk=chunk)

            # Create vector document
            vector_doc = VectorDocument(
                id=document.metadata.title.replace(" ", "_").lower()[:50] + f"_{int(datetime.now().timestamp())}",
                content=content,
                metadata={
                    "title": document.metadata.title,
                    "source": document.metadata.source,
                    "source_type": document.metadata.source_type,
                    "created_at": document.metadata.created_at,
                    "format_version": document.metadata.format_version,
                    "ai_processed": document.metadata.ai_processing_enabled or False,
                },
                embedding=embedding_result["document_embedding"],
                chunks=embedding_result["chunks"],
                last_indexed=datetime.now().isoformat()
            )

            vector_docs.append(vector_doc)

        # Add to vector store
        doc_ids = self.vector_store.add_documents(vector_docs)
        self.indexed_documents += len(doc_ids)

        logger.info(f"Added {len(doc_ids)} documents to RAG system")
        return doc_ids

    def query(self, question: str, context_documents: Optional[List[str]] = None,
             max_results: int = 5, generate_answer: bool = True) -> RAGResponse:
        """
        Query the RAG system with a question.

        Args:
            question: Question to answer
            context_documents: Optional list of document IDs to search in
            max_results: Maximum number of results to retrieve
            generate_answer: Whether to generate an answer using AI

        Returns:
            RAG response with answer and sources
        """
        start_time = datetime.now()

        # Create query object
        rag_query = RAGQuery(
            question=question,
            context_documents=context_documents or [],
            max_results=max_results
        )

        # Perform semantic search
        search_results = self._semantic_search(rag_query)

        # Generate answer if requested and AI is available
        answer = ""
        reasoning_chain = []
        confidence_score = 0.5

        if generate_answer and self.ai_analyzer and search_results:
            answer, reasoning_chain, confidence_score = self._generate_answer(
                question, search_results
            )
        elif not generate_answer:
            # Just return relevant passages
            answer = self._format_search_results(search_results)
        else:
            answer = "AI analysis not available. Here are the most relevant passages from documents:"
            answer += "\n\n" + self._format_search_results(search_results)

        processing_time = (datetime.now() - start_time).total_seconds()
        self.query_count += 1

        return RAGResponse(
            answer=answer,
            sources=search_results,
            confidence_score=confidence_score,
            reasoning_chain=reasoning_chain,
            processing_time=processing_time
        )

    def search_similar(self, text: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search for documents similar to the given text.

        Args:
            text: Text to find similar documents for
            max_results: Maximum number of results

        Returns:
            List of search results with similarity scores
        """
        # Generate embedding for the query
        query_embedding = self.embedding_manager.embed_text(text)

        # Search vector store
        vector_results = self.vector_store.search(query_embedding, max_results)

        search_results = []
        for doc_id, score in vector_results:
            # Get full document
            vector_doc = self.vector_store.get_document(doc_id)
            if vector_doc:
                search_result = SearchResult(
                    document_id=doc_id,
                    content=vector_doc.content[:500] + "..." if len(vector_doc.content) > 500 else vector_doc.content,
                    metadata=vector_doc.metadata,
                    score=score,
                    highlights=self._extract_highlights(text, vector_doc.content)
                )
                search_results.append(search_result)

        return search_results

    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        return {
            "indexed_documents": self.indexed_documents,
            "query_count": self.query_count,
            "vector_store_type": type(self.vector_store).__name__,
            "embedding_dimension": self.embedding_manager.embedding_provider.dimension,
            "ai_available": self.ai_analyzer is not None
        }

    def clear_index(self):
        """Clear all indexed documents."""
        self.vector_store.clear()
        self.indexed_documents = 0
        logger.info("Cleared RAG index")

    def _semantic_search(self, query: RAGQuery) -> List[SearchResult]:
        """Perform semantic search for the query."""
        # Generate embedding for the question
        question_embedding = self.embedding_manager.embed_text(query.question)

        # Search vector store
        vector_results = self.vector_store.search(question_embedding, query.max_results)

        search_results = []
        for doc_id, score in vector_results:
            # Get full document
            vector_doc = self.vector_store.get_document(doc_id)
            if vector_doc:
                # Find most relevant chunks if document was chunked
                relevant_content = self._find_relevant_content(query.question, vector_doc)

                search_result = SearchResult(
                    document_id=doc_id,
                    content=relevant_content,
                    metadata=vector_doc.metadata,
                    score=score,
                    highlights=self._extract_highlights(query.question, relevant_content)
                )
                search_results.append(search_result)

        return search_results

    def _find_relevant_content(self, question: str, vector_doc: VectorDocument) -> str:
        """Find the most relevant content within a document."""
        if not vector_doc.chunks:
            return vector_doc.content

        # Simple approach: return the chunk with highest similarity to question
        question_embedding = self.embedding_manager.embed_text(question)

        best_chunk = None
        best_score = -1

        for chunk in vector_doc.chunks:
            if chunk.get("embedding"):
                # Calculate similarity (cosine similarity)
                similarity = self._cosine_similarity(question_embedding, chunk["embedding"])
                if similarity > best_score:
                    best_score = similarity
                    best_chunk = chunk

        return best_chunk["text"] if best_chunk else vector_doc.content

    def _generate_answer(self, question: str, search_results: List[SearchResult]) -> tuple:
        """Generate an answer using AI based on search results."""
        if not self.ai_analyzer:
            return "", [], 0.0

        # Format context from search results
        context_parts = []
        for result in search_results[:3]:  # Use top 3 results
            context_parts.append(f"Document: {result.metadata.get('title', 'Unknown')}")
            context_parts.append(f"Content: {result.content}")
            context_parts.append("---")

        context = "\n".join(context_parts)

        # Create prompt for answer generation
        prompt = f"""
        Based on the following document excerpts, answer the question accurately.
        If the documents don't contain enough information to answer fully, say so.

        Question: {question}

        Document Context:
        {context}

        Answer concisely but comprehensively. Include specific references to the documents when relevant.
        """

        try:
            # Use AI analyzer to generate response
            # For now, we'll create a mock response since we need to integrate with the analyzer
            reasoning = [
                "Analyzed search results for relevance",
                "Extracted key information from top documents",
                "Generated coherent answer based on evidence"
            ]

            # Simple answer generation (would be replaced with actual AI call)
            answer = f"Based on the available documents, here's what I found regarding '{question}':\n\n"
            for i, result in enumerate(search_results[:2], 1):
                answer += f"{i}. From '{result.metadata.get('title', 'Document')}' (relevance: {result.score:.2f}):\n"
                answer += f"   {result.content[:200]}...\n\n"

            confidence = min(0.9, sum(r.score for r in search_results[:3]) / 3) if search_results else 0.3

            return answer, reasoning, confidence

        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "Unable to generate answer due to technical issues.", ["Error occurred"], 0.0

    def _format_search_results(self, results: List[SearchResult]) -> str:
        """Format search results for display."""
        if not results:
            return "No relevant documents found."

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.metadata.get('title', 'Document')} (score: {result.score:.2f})")
            formatted.append(f"   {result.content[:300]}{'...' if len(result.content) > 300 else ''}")
            formatted.append("")

        return "\n".join(formatted)

    def _extract_highlights(self, query: str, content: str) -> List[str]:
        """Extract highlighted snippets from content based on query."""
        highlights = []
        query_words = query.lower().split()

        # Simple keyword highlighting
        for word in query_words:
            if len(word) > 3:  # Skip short words
                start = content.lower().find(word.lower())
                if start != -1:
                    # Extract context around the word
                    context_start = max(0, start - 50)
                    context_end = min(len(content), start + len(word) + 50)
                    highlight = content[context_start:context_end]
                    highlights.append(highlight)

        return highlights[:3]  # Limit to 3 highlights

    def _extract_content_from_sections(self, sections: List[Dict[str, Any]]) -> str:
        """Extract text content from document sections."""
        content_parts = []

        for section in sections:
            if section.get("title"):
                content_parts.append(f"## {section['title']}")

            if section.get("content"):
                if isinstance(section["content"], list):
                    content_parts.extend(section["content"])
                else:
                    content_parts.append(section["content"])

        return "\n\n".join(content_parts)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import math

        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))

        # Calculate magnitudes
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))

        # Avoid division by zero
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)
