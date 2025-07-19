"""
Create RAG Database Chain

This chain processes PDF files and creates a vector database for RAG functionality.
"""

from typing import Any, Dict

from langchain_core.runnables import RunnableLambda

from services.pdf_processor import pdf_processor
from services.vector_store import vector_store_service
from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def create_rag_db_logic(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process PDFs and create RAG vector database.

    Args:
        input_data: Dictionary containing optional parameters:
            - pdf_directory: Directory containing PDF files (optional)
            - clear_existing: Whether to clear existing documents (optional)

    Returns:
        Dictionary with processing results
    """
    config = load_config("rag")

    # Get PDF directory from input or config
    pdf_directory = input_data.get(
        "pdf_directory", config.get("pdf_directory", "data/pdfs")
    )
    clear_existing = input_data.get("clear_existing", False)

    logger.info("--- 📚 Creating RAG Database ---")
    logger.info(f"PDF Directory: {pdf_directory}")

    try:
        # Clear existing documents if requested
        if clear_existing:
            logger.info("Clearing existing documents from vector store")
            vector_store_service.clear_collection()

        # Process PDF files
        logger.info("Processing PDF files...")
        documents = pdf_processor.process_pdf_directory(pdf_directory)

        if not documents:
            logger.warning("No documents found to process")
            return {
                "status": "warning",
                "message": "No PDF files found to process",
                "documents_processed": 0,
                "pdf_directory": pdf_directory,
            }

        # Add documents to vector store
        logger.info("Adding documents to vector store...")
        vector_store_service.add_documents(documents)

        # Get collection info
        collection_info = vector_store_service.get_collection_info()

        logger.info("✅ RAG Database created successfully")

        return {
            "status": "success",
            "message": "RAG Database created successfully",
            "documents_processed": len(documents),
            "pdf_directory": pdf_directory,
            "collection_info": collection_info,
        }

    except Exception as e:
        logger.error(f"Error creating RAG database: {e}")
        return {
            "status": "error",
            "message": f"Error creating RAG database: {str(e)}",
            "documents_processed": 0,
            "pdf_directory": pdf_directory,
        }


# Create the chain
create_rag_db_chain = RunnableLambda(create_rag_db_logic)
