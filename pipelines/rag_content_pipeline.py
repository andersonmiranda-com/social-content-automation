"""
RAG Content Pipeline

This pipeline generates content using RAG and publishes it to Telegram.
The pipeline includes:
1. Topic selection from topics file
2. Content generation using RAG
3. Content formatting for Telegram
4. Publication to Telegram
"""

from langchain_core.runnables import RunnablePassthrough

from chains.apply_overlay_chain import apply_overlay_chain
from chains.generate_dalle_image import generate_dalle_image_chain
from chains.rag_content_chain import rag_content_chain
from chains.select_topic_rag_chain import select_topic_rag_chain
from chains.telegram_publish_chain import (
    format_telegram_content_chain,
    publish_to_telegram_chain,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_pipeline_result(result: dict) -> dict:
    """
    Validate the pipeline execution result.

    Args:
        result: Result from the pipeline

    Returns:
        Validation result
    """
    # Check if all steps were successful
    topic_selection = result.get("topic_selection", {})
    content_generation = result.get("content_generation", {})
    image_generation = result.get("image_generation", {})
    overlay_application = result.get("overlay_application", {})
    content_formatting = result.get("content_formatting", {})
    telegram_publication = result.get("telegram_publication", {})

    all_successful = (
        topic_selection.get("status") == "success"
        and content_generation.get("status") == "success"
        and image_generation.get("status") == "success"
        and overlay_application.get("status") == "success"
        and content_formatting.get("status") == "success"
        and telegram_publication.get("status") == "success"
    )

    if all_successful:
        logger.info("✅ Pipeline execution completed successfully!")
        validation_result = {
            "status": "success",
            "message": "All pipeline steps completed successfully",
        }
    else:
        logger.error("❌ Pipeline execution failed")
        validation_result = {
            "status": "error",
            "message": "One or more pipeline steps failed",
        }

    return validation_result


# Create the complete pipeline
rag_content_pipeline = (
    # Step 1: Select random topic
    RunnablePassthrough.assign(topic_selection=select_topic_rag_chain)
    # Step 2: Generate content using RAG
    | RunnablePassthrough.assign(
        content_generation=lambda x: rag_content_chain.invoke(
            {"selected_topic": x["topic_selection"]["selected_topic"]}
        )
    )
    # Step 3: Generate image with DALL-E-3
    | RunnablePassthrough.assign(
        image_generation=lambda x: generate_dalle_image_chain.invoke(
            {
                "generated_content": x["content_generation"]["generated_content"],
                "topic": x["topic_selection"]["selected_topic"],
            }
        )
    )
    # Step 4: Apply overlay to image
    | RunnablePassthrough.assign(
        overlay_application=lambda x: apply_overlay_chain.invoke(
            {
                "image_data": x["image_generation"]["image_data"],
            }
        )
    )
    # Step 5: Format content for Telegram
    | RunnablePassthrough.assign(
        content_formatting=lambda x: format_telegram_content_chain.invoke(
            {
                "generated_content": x["content_generation"]["generated_content"],
                "quote": x["content_generation"]["quote"],
                "topic": x["topic_selection"]["selected_topic"],
            }
        )
    )
    # Step 6: Publish to Telegram
    | RunnablePassthrough.assign(
        telegram_publication=lambda x: publish_to_telegram_chain.invoke(
            {
                "formatted_message": x["content_formatting"]["formatted_message"],
                "image_url": x["overlay_application"]["overlaid_image"],
            }
        )
    )
    # Step 7: Validate results
    | RunnablePassthrough.assign(validation=validate_pipeline_result)
)
