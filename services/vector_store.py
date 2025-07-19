"""
Vector Store Service

This module manages the vector database for RAG functionality using ChromaDB.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class VectorStoreService:
    """Service for managing vector database operations."""

    def __init__(self):
        """Initialize the vector store service."""
        self.config = load_config("rag")
        self.vector_db_path = self.config.get("vector_db_path", "data/vector_db")
        self.collection_name = self.config.get("collection_name", "pdf_documents")

        # Ensure vector DB directory exists
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=self.config.get("embedding_model", "text-embedding-3-small")
        )

        # Initialize vector store
        self._init_vector_store()

    def _init_vector_store(self):
        """Initialize or load the ChromaDB vector store."""
        try:
            self.vector_store = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.vector_db_path,
            )
            logger.info(f"Vector store initialized at {self.vector_db_path}")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            raise

    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store in batches.

        Args:
            documents: List of Document objects to add
        """
        if not documents:
            logger.warning("No documents provided to add to vector store")
            return

        try:
            # Process documents in batches to avoid batch size limits
            batch_size = self.config.get("batch_size", 1000)
            total_documents = len(documents)

            logger.info(
                f"Adding {total_documents} documents in batches of {batch_size}"
            )

            for i in range(0, total_documents, batch_size):
                batch = documents[i : i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_documents + batch_size - 1) // batch_size

                logger.info(
                    f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents)"
                )

                # Add batch to vector store
                self.vector_store.add_documents(batch)

                logger.info(f"✅ Batch {batch_num}/{total_batches} completed")

            logger.info(
                f"✅ Successfully added all {total_documents} documents to vector store"
            )

        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            raise

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        Perform similarity search in the vector store.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.info(
                f"Found {len(results)} similar documents for query: {query[:50]}..."
            )
            return results

        except Exception as e:
            logger.error(f"Error performing similarity search: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the current collection.

        Returns:
            Dictionary with collection information
        """
        try:
            collection = self.vector_store._collection
            count = collection.count()

            info = {
                "collection_name": self.collection_name,
                "document_count": count,
                "vector_db_path": self.vector_db_path,
            }

            logger.info(f"Collection info: {info}")
            return info

        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            raise

    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        try:
            # Get all document IDs and delete them
            collection = self.vector_store._collection
            # Get all documents to find their IDs
            results = collection.get()
            if results and results.get("ids"):
                collection.delete(ids=results["ids"])
                logger.info(
                    f"Cleared {len(results['ids'])} documents from vector store"
                )
            else:
                logger.info("No documents to clear from vector store")

        except Exception as e:
            logger.error(f"Error clearing collection: {e}")
            raise

    def delete_documents_by_source(self, source_path: str) -> None:
        """
        Delete documents from a specific source.

        Args:
            source_path: Path of the source file to delete documents from
        """
        try:
            # Delete documents where source matches
            self.vector_store._collection.delete(where={"source": source_path})
            logger.info(f"Deleted documents from source: {source_path}")

        except Exception as e:
            logger.error(f"Error deleting documents from source {source_path}: {e}")
            raise


# Singleton instance
vector_store_service = VectorStoreService()
