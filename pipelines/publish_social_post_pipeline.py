"""
Main pipeline for publishing content to social media.

This pipeline orchestrates the process of:
1. Selecting content from a source (e.g., Google Sheets).
2. Generating a Canva design URL if needed.
3. Uploading the final image to a persistent store (Cloudinary).
4. Publishing the content to specified social media platforms.
5. Updating the status of the content to mark it as published.
"""

from typing import Dict, Any

from langchain.schema.runnable import Runnable, RunnableBranch, RunnablePassthrough

from chains.get_content_chain import get_content_chain
from chains.create_canva_design_chain import create_canva_design_chain
from chains.upload_chain import upload_chain
from chains.publish_linkedin_post import linkedin_post_chain  # Import the new chain
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _should_generate_image(data: Dict[str, Any]) -> bool:
    """Returns True if a new image should be generated."""
    # The data is the post itself, no need to look for a nested key.
    return not data.get("image_ready_url")


def _prepare_data_for_upload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Selects the correct image URL to be uploaded to Cloudinary.
    The URL can be a temporary one from Canva or a pre-existing one.
    """
    # If a new design was created, use its download URL and specify the published folder.
    if "canva_download_url" in data:
        logger.info(
            "Preparing Canva URL for Cloudinary upload to 'social_published' folder."
        )
        return {"image_url": data["canva_download_url"], "folder": "social_published"}

    # Otherwise, use the URL that was already in the sheet (folder will be default).
    logger.info("Preparing existing image URL for Cloudinary upload.")
    return {"image_url": data.get("image_ready_url")}


# Conditional logic: Decide whether to generate a new image or use an existing one.
image_generation_branch = RunnableBranch(
    (
        _should_generate_image,  # Condition: if image_ready_url is empty
        create_canva_design_chain,  # If true, run the Canva chain
    ),
    RunnablePassthrough(),  # If false, just pass the data through
)


def _route(data: Dict[str, Any]) -> Runnable:
    # If get_content_chain returns an empty dict, it means no post was found.
    if not data:
        return RunnablePassthrough.assign(
            final_result=lambda x: "Pipeline stopped: No content found."
        )

    # The main flow if a post is found.
    main_flow = (
        RunnablePassthrough.assign(canva_result=image_generation_branch)
        | (lambda x: {**x, **x.pop("canva_result")})
        | RunnablePassthrough.assign(upload_input=_prepare_data_for_upload)
        | RunnablePassthrough.assign(
            upload_result=lambda x: upload_chain.invoke(x["upload_input"])
        )
        # --- Add LinkedIn Publishing Step ---
        | RunnablePassthrough.assign(
            linkedin_result=lambda x: linkedin_post_chain.invoke(
                {
                    "content": x.get("content"),
                    "hashtags": x.get("hashtags"),
                    "image_url": x.get("upload_result", {}).get("image_url"),
                }
            )
        )
    )
    return main_flow


# Full pipeline definition
publish_social_post_pipeline: Runnable = (
    # 1. Get the content
    get_content_chain
    # 2. Route to the correct path based on whether content was found
    | _route
    # 3. Merge the results for a clean final output
    | (
        lambda x: {
            **x,
            "cloudinary_url": x.get("upload_result", {}).get("image_url"),
            "linkedin_post_id": x.get("linkedin_result", {}).get("linkedin_post_id"),
            "status": x.get("final_result", "completed"),
        }
    )
)

if __name__ == "__main__":
    import json

    logger.info("🚀 Starting social post publishing pipeline...")
    final_result = publish_social_post_pipeline.invoke({})
    logger.info("✅ Pipeline finished.")

    # Pretty-print the final result
    print(json.dumps(final_result, indent=4))
