"""
Fake Cloudinary Tool
- Simulates uploading an image URL and returns a new "cloudinary" URL.
"""

from langchain_core.runnables import RunnableLambda
from services.cloudinary_client import cloudinary_client
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _is_base64(s: str) -> bool:
    """Check if a string is a valid base64 encoded string."""
    import base64
    import re

    # This regex is a simple check for base64 characters.
    # A more robust check might be needed for production.
    if not isinstance(s, str) or not re.match(r"^[A-Za-z0-9+/=]+$", s):
        return False
    try:
        base64.b64decode(s)
        return True
    except (ValueError, TypeError):
        return False


def _upload_image_logic(data: dict) -> dict:
    """
    Receives image data (URL), uploads it to Cloudinary, and returns the new URL.
    Optionally accepts a 'folder' to override the default.
    """
    image_url = data.get("image_url")
    if not image_url:
        raise ValueError("No 'image_url' provided for upload.")

    folder = data.get("folder")  # Can be None, client will use default

    logger.info("--- ☁️ Uploading to Cloudinary ---")

    upload_source = image_url
    if _is_base64(image_url):
        logger.info("   Uploading from Base64 data.")
        upload_source = f"data:image/png;base64,{image_url}"
    else:
        logger.info(f"   Uploading from URL: {image_url}")

    upload_result = cloudinary_client.upload(image_url=upload_source, folder=folder)

    # Extract the secure URL from the response
    cloudinary_url = upload_result.get("secure_url")
    if not cloudinary_url:
        raise ValueError("Cloudinary upload failed, no 'secure_url' in response.")

    logger.info(f"   ✅  Upload complete. New URL: {cloudinary_url}")

    # Return a generic key, not a service-specific one.
    return {"image_url": cloudinary_url}


upload_to_cloudinary_chain = RunnableLambda(_upload_image_logic)
