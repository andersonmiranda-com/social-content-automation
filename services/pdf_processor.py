"""
PDF Processor Service

This module handles PDF file processing, including text extraction and chunking
for vector database storage.
"""

import os
from pathlib import Path
from typing import Any, Dict, List

import PyPDF2
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFProcessor:
    """Service for processing PDF files and extracting text content."""

    def __init__(self):
        """Initialize the PDF processor with configuration."""
        self.config = load_config("rag")
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.get("chunk_size", 1000),
            chunk_overlap=self.config.get("chunk_overlap", 200),
            length_function=len,
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content
        """
        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""

                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"

                logger.info(f"Extracted text from {pdf_path}: {len(text)} characters")
                return text

        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            raise

    def process_pdf_file(self, pdf_path: str) -> List[Document]:
        """
        Process a single PDF file and return chunked documents.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of Document objects ready for vector storage
        """
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)

        # Create metadata
        metadata = {
            "source": pdf_path,
            "filename": Path(pdf_path).name,
            "file_type": "pdf",
        }

        # Split text into chunks
        documents = self.text_splitter.create_documents(
            texts=[text], metadatas=[metadata]
        )

        logger.info(f"Created {len(documents)} chunks from {pdf_path}")
        return documents

    def process_pdf_directory(self, pdf_dir: str) -> List[Document]:
        """
        Process all PDF files in a directory.

        Args:
            pdf_dir: Directory containing PDF files

        Returns:
            List of all Document objects from all PDFs
        """
        pdf_dir_path = Path(pdf_dir)
        if not pdf_dir_path.exists():
            raise ValueError(f"PDF directory does not exist: {pdf_dir}")

        all_documents = []
        pdf_files = list(pdf_dir_path.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return all_documents

        logger.info(f"Found {len(pdf_files)} PDF files to process")

        for pdf_file in pdf_files:
            try:
                documents = self.process_pdf_file(str(pdf_file))
                all_documents.extend(documents)
                logger.info(f"Processed {pdf_file.name}: {len(documents)} chunks")
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
                continue

        logger.info(f"Total documents created: {len(all_documents)}")
        return all_documents


# Singleton instance
pdf_processor = PDFProcessor()
