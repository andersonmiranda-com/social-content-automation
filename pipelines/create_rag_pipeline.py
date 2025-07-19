"""
Create RAG Database Pipeline

This pipeline processes PDF files and creates a vector database for RAG functionality.
The pipeline includes:
1. PDF processing and text extraction
2. Text chunking
3. Vector embedding and storage
4. Database validation
"""

from langchain_core.runnables import RunnablePassthrough

from chains.create_rag_db_chain import create_rag_db_chain
from utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_rag_db_logic(result: dict) -> dict:
    """
    Validate the created RAG database.

    Args:
        result: Result from create_rag_db_chain

    Returns:
        Validation result
    """
    if result.get("status") == "success":
        collection_info = result.get("collection_info", {})
        doc_count = collection_info.get("document_count", 0)

        if doc_count > 0:
            logger.info(
                f"✅ RAG Database validation successful: {doc_count} documents stored"
            )
            result["validation"] = {
                "status": "success",
                "document_count": doc_count,
                "message": f"Database contains {doc_count} documents",
            }
        else:
            logger.warning("⚠️ RAG Database validation warning: No documents found")
            result["validation"] = {
                "status": "warning",
                "document_count": 0,
                "message": "Database is empty",
            }
    else:
        logger.error("❌ RAG Database validation failed")
        result["validation"] = {
            "status": "error",
            "message": "Database creation failed",
        }

    return result


# Create the complete pipeline
create_rag_pipeline = (
    # Step 1: Create RAG database
    create_rag_db_chain
    # Step 2: Validate the created database
    | RunnablePassthrough.assign(validation=validate_rag_db_logic)
)
