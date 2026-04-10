"""
RAG (Retrieval-Augmented Generation) system for the Smart Escalation API.

This module provides functionality to load help articles, generate embeddings,
build a FAISS vector store, and perform similarity search for customer questions.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from src.chunking import chunk_text


@dataclass
class RetrievedChunk:
    """Represents a chunk retrieved from the vector store."""
    content: str
    score: float  # Cosine similarity score
    source: str   # Help article filename
    chunk_id: int
    position: int


class RAGSystem:
    """
    RAG system that loads help articles, generates embeddings, and performs similarity search.
    
    The system uses sentence-transformers for embeddings and FAISS for efficient
    similarity search over article chunks.
    """
    
    def __init__(
        self,
        articles_dir: str = "data/articles",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize the RAG system.
        
        Args:
            articles_dir: Directory containing help article markdown files
            embedding_model: Name of the sentence-transformers model to use
            chunk_size: Maximum size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.articles_dir = articles_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model}...")
        self.embedding_model = SentenceTransformer(embedding_model)
        self.embedding_dim = self.embedding_model.get_embedding_dimension()
        
        # Storage for chunks and metadata
        self.chunks: List[Dict[str, Any]] = []
        self.index: Optional[faiss.Index] = None
        
        # Load articles and build index
        self._load_articles()
        self._build_index()
        
        print(f"RAG system initialized with {len(self.chunks)} chunks")
    
    def _load_articles(self) -> None:
        """
        Load all markdown files from the articles directory and chunk them.
        
        Reads all .md files from the articles directory, chunks each article,
        and stores the chunks with metadata.
        """
        if not os.path.exists(self.articles_dir):
            raise FileNotFoundError(f"Articles directory not found: {self.articles_dir}")
        
        article_files = [
            f for f in os.listdir(self.articles_dir)
            if f.endswith('.md') and f != '.gitkeep'
        ]
        
        if not article_files:
            raise ValueError(f"No markdown files found in {self.articles_dir}")
        
        print(f"Loading {len(article_files)} articles from {self.articles_dir}...")
        
        for filename in sorted(article_files):
            filepath = os.path.join(self.articles_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Chunk the article
            article_chunks = chunk_text(
                text=content,
                source_article=filename,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            
            self.chunks.extend(article_chunks)
            print(f"  Loaded {filename}: {len(article_chunks)} chunks")
    
    def _build_index(self) -> None:
        """
        Generate embeddings for all chunks and build FAISS index.
        
        Creates embeddings for each chunk using the sentence-transformers model
        and builds an in-memory FAISS index for efficient similarity search.
        """
        if not self.chunks:
            raise ValueError("No chunks available to build index")
        
        print("Generating embeddings for all chunks...")
        
        # Extract chunk contents for embedding
        chunk_texts = [chunk['content'] for chunk in self.chunks]
        
        # Generate embeddings in batch
        embeddings = self.embedding_model.encode(
            chunk_texts,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        # Normalize embeddings for cosine similarity
        # FAISS inner product with normalized vectors = cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Build FAISS index (using IndexFlatIP for inner product / cosine similarity)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings.astype('float32'))
        
        print(f"FAISS index built with {self.index.ntotal} vectors")
    
    def retrieve(self, question: str, top_k: int = 3) -> List[RetrievedChunk]:
        """
        Retrieve the most relevant chunks for a given question.
        
        Args:
            question: The customer question to search for
            top_k: Number of top chunks to retrieve (default: 3)
            
        Returns:
            List of RetrievedChunk objects ordered by descending relevance score
            
        Example:
            >>> rag = RAGSystem()
            >>> chunks = rag.retrieve("How do I reset my password?", top_k=3)
            >>> chunks[0].content
            'To reset your password...'
            >>> chunks[0].score
            0.85
        """
        if self.index is None:
            raise RuntimeError("Index not built. Call _build_index() first.")
        
        if not question or not question.strip():
            return []
        
        # Limit top_k to available chunks
        actual_k = min(top_k, len(self.chunks))
        
        if actual_k == 0:
            return []
        
        # Generate embedding for the question
        question_embedding = self.embedding_model.encode(
            [question],
            convert_to_numpy=True
        )
        
        # Normalize for cosine similarity
        faiss.normalize_L2(question_embedding)
        
        # Search the index
        scores, indices = self.index.search(
            question_embedding.astype('float32'),
            actual_k
        )
        
        # Build result list
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            
            chunk = self.chunks[idx]
            results.append(RetrievedChunk(
                content=chunk['content'],
                score=float(score),
                source=chunk['source'],
                chunk_id=chunk['chunk_id'],
                position=chunk['position']
            ))
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dictionary with system statistics including number of chunks,
            articles, and index information
        """
        sources = set(chunk['source'] for chunk in self.chunks)
        
        return {
            'total_chunks': len(self.chunks),
            'total_articles': len(sources),
            'articles': sorted(sources),
            'embedding_dim': self.embedding_dim,
            'index_size': self.index.ntotal if self.index else 0
        }
