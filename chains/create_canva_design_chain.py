"""
Chain for creating a design using the Canva API.

This chain handles the process of:
1. Uploading a base image asset to Canva.
2. Populating a brand template with text and the asset.
3. Exporting the final design as a PNG.
4. Returning the download URL for the generated image.
"""

import asyncio
import base64
from typing import Dict, Any

import httpx
from langchain.schema.runnable import RunnableLambda

from services.canva_client import CanvaClient
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Constants for Canva polling
FIXED_WAIT_SECONDS = 10


async def create_canva_design(post_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrates the Canva API to create a new image and return its download URL.

    Args:
        post_data: A dictionary containing the post details, including
                   'image_url', 'title', and 'subtitle'.

    Returns:
        A dictionary containing the 'canva_download_url' and 'canva_design_id'.
    """
    logger.info("Starting Canva image creation process...")
    canva_client = CanvaClient()

    image_url = post_data.get("image_url")
    if not image_url:
        raise ValueError("Input 'post_data' must contain an 'image_url'.")

    # 1. Download the base image
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
        response.raise_for_status()
        image_content = response.content
    logger.info(f"Successfully downloaded base image from {image_url}")

    # 2. Upload asset to Canva and wait
    row_number = post_data.get("row_number", post_data.get("id", "unknown"))
    name_base64 = base64.b64encode(f"image_{row_number}".encode()).decode()
    upload_job = await canva_client.upload_asset(
        file_content=image_content, name_base64=name_base64
    )
    upload_job_id = upload_job.get("job", {}).get("id")

    logger.info(
        f"Waiting {FIXED_WAIT_SECONDS}s for asset job {upload_job_id} to process..."
    )
    await asyncio.sleep(FIXED_WAIT_SECONDS)

    upload_status = await canva_client.get_asset_upload_status(upload_job_id)
    asset_id = upload_status.get("job", {}).get("asset", {}).get("id")
    if not asset_id:
        raise RuntimeError(
            f"Could not get asset_id from Canva upload job. Full response: {upload_status}"
        )

    # 3. Autofill template and wait
    title = post_data.get("title", "")
    subtitle = post_data.get("subtitle", "")
    autofill_job = await canva_client.autofill_template(asset_id, title, subtitle)
    autofill_job_id = autofill_job.get("job", {}).get("id")

    logger.info(
        f"Waiting {FIXED_WAIT_SECONDS}s for autofill job {autofill_job_id} to process..."
    )
    await asyncio.sleep(FIXED_WAIT_SECONDS)

    autofill_status = await canva_client.get_autofill_status(autofill_job_id)
    design_id = (
        autofill_status.get("job", {}).get("result", {}).get("design", {}).get("id")
    )
    if not design_id:
        raise RuntimeError(
            f"Could not get design_id from Canva autofill job. Full response: {autofill_status}"
        )

    # 4. Export the final design and wait
    export_job = await canva_client.export_design(design_id)
    export_job_id = export_job.get("job", {}).get("id")

    logger.info(
        f"Waiting {FIXED_WAIT_SECONDS}s for export job {export_job_id} to process..."
    )
    await asyncio.sleep(FIXED_WAIT_SECONDS)

    export_status = await canva_client.get_export_status(export_job_id)
    download_url = export_status.get("job", {}).get("urls", [])[0]
    if not download_url:
        raise RuntimeError(
            f"Could not get download_url from Canva export job. Full response: {export_status}"
        )

    logger.info(f"Successfully generated Canva design. Download URL: {download_url}")

    return {"canva_download_url": download_url, "canva_design_id": design_id}


create_canva_design_chain = RunnableLambda(create_canva_design)
