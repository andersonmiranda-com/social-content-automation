"""
Main pipeline for publishing content to social media.

This pipeline orchestrates the process of:
1. Selecting content from a source (e.g., Google Sheets).
2. Generating a Canva design URL if needed.
3. Uploading the final image to a persistent store (Cloudinary).
4. Publishing the content to specified social media platforms.
5. Updating the status of the content to mark it as published.
"""

from operator import itemgetter
from typing import Dict, Any

from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from chains.get_content_chain import get_content_chain
from chains.create_canva_design_chain import create_canva_design_chain
from chains.upload_chain import upload_chain
from chains.publish_linkedin_post import linkedin_post_chain
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _stop_if_no_content(post: Dict[str, Any]) -> Dict[str, Any]:
    """Stops the pipeline if no content is found, otherwise passes it through."""
    if not post:
        logger.warning("Pipeline stopping: No content found to publish.")
        return {"status": "no_content", "message": "No content found to publish."}
    return post


def _create_image_if_needed(post: Dict[str, Any]) -> Dict[str, Any]:
    """Runs the Canva chain only if 'image_ready_url' is missing."""
    # If the pipeline was stopped, just pass the data through.
    if post.get("status") == "no_content":
        return post

    if not post.get("image_ready_url"):
        logger.info("Image URL not found. Generating a new image with Canva.")
        canva_result = create_canva_design_chain.invoke(post)
        # Merge the Canva result back into the main dictionary.
        return {**post, **canva_result}

    logger.info("Using existing image URL for the post.")
    return post


def _prepare_upload_input(post: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares the dictionary for the Cloudinary upload chain."""
    if post.get("status") == "no_content":
        return {}  # Return empty to avoid invoking the chain.

    # Choose the Canva URL if it exists; otherwise, use the pre-existing URL.
    image_to_upload = post.get("canva_download_url") or post.get("image_ready_url")
    return {"image_url": image_to_upload, "folder": "social_published"}


def _prepare_linkedin_input(post: Dict[str, Any]) -> Dict[str, Any]:
    """Prepares the dictionary for the LinkedIn publishing chain."""
    if post.get("status") == "no_content":
        return {}  # Return empty to avoid invoking the chain.

    # The image_url for LinkedIn comes from the Cloudinary upload result.
    image_url = post.get("upload_result", {}).get("image_url")
    return {
        "content": post.get("content"),
        "hashtags": post.get("hashtags"),
        "image_url": image_url,
    }


def _format_final_output(post: Dict[str, Any]) -> Dict[str, Any]:
    """Cleans and formats the final dictionary returned by the pipeline."""
    # If the pipeline was stopped, return the stop message as is.
    if post.get("status") == "no_content":
        return post

    return {
        "content": post.get("content"),
        "hashtags": post.get("hashtags"),
        "image_url": post.get("upload_result", {}).get("image_url"),
        "linkedin_post_id": post.get("linkedin_result", {}).get("linkedin_post_id"),
        "status": post.get("linkedin_result", {}).get("status", "completed"),
    }


publish_social_post_pipeline = (
    # 1. Get content from Google Sheets.
    get_content_chain
    # 2. Check if content exists; if not, stop the pipeline.
    | RunnableLambda(_stop_if_no_content)
    # 3. Create an image with Canva if it's needed.
    | RunnableLambda(_create_image_if_needed)
    # 4. Upload the final image to Cloudinary.
    | RunnablePassthrough.assign(
        upload_result=(RunnableLambda(_prepare_upload_input) | upload_chain)
    )
    # 5. Publish the post to LinkedIn.
    | RunnablePassthrough.assign(
        linkedin_result=(RunnableLambda(_prepare_linkedin_input) | linkedin_post_chain)
    )
    # 6. Format the final output for clarity.
    | RunnableLambda(_format_final_output)
)
