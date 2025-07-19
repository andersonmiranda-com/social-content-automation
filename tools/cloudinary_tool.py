"""
Fake Cloudinary Tool
- Simulates uploading an image URL and returns a new "cloudinary" URL.
"""

import re

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


def _apply_overlay_logic(data: dict) -> dict:
    """
    Uploads image to Cloudinary with overlay applied during upload.
    """
    from utils.config_loader import load_config

    image_url = data.get("image_url")

    if not image_url:
        raise ValueError("No 'image_url' provided for overlay.")

    # Load overlay configuration
    config = load_config("overlay")

    if not config.get("enabled", True):
        logger.info("--- 🖼️ Overlay disabled, uploading without overlay ---")
        # Upload without overlay
        upload_result = cloudinary_client.upload(image_url=image_url)
        if upload_result.get("secure_url"):
            return {
                "status": "success",
                "overlaid_url": upload_result["secure_url"],
                "original_url": image_url,
                "overlay_applied": False,
            }
        else:
            return {
                "status": "error",
                "message": "Upload failed",
                "overlaid_url": image_url,
            }

    position = config.get("position", "top_left")
    opacity = config.get("opacity", 0.6)
    size_percentage = config.get("size_percentage", 12)
    offset_x = config.get("offset_x", 0.03)
    offset_y = config.get("offset_y", 0.04)
    overlay_image = config.get("overlay_image", "social:Icon_Blanco_o3u4wy")

    logger.info("--- 🖼️ Uploading to Cloudinary with overlay ---")
    logger.info(f"   Position: {position}")
    logger.info(f"   Opacity: {opacity}")
    logger.info(f"   Size: {size_percentage}%")
    logger.info(f"   Offset: x={offset_x}, y={offset_y}")
    logger.info(f"   Overlay image: {overlay_image}")

    try:
        # Upload with overlay transformation
        # Map position to Cloudinary gravity values
        gravity_map = {
            "bottom_right": "south_east",
            "top_right": "north_east",
            "bottom_left": "south_west",
            "top_left": "north_west",
            "center": "center",
        }

        cloudinary_gravity = gravity_map.get(position, "north_west")

        # Build transformation with the new overlay parameters
        transformation = [
            {
                "overlay": overlay_image,
                "width": f"fl_relative,w_{size_percentage/100:.2f}",
                "opacity": int(opacity * 100),
                "gravity": cloudinary_gravity,
                "x": offset_x,
                "y": offset_y,
            }
        ]

        upload_options = {
            "folder": "social",
            "transformation": transformation,
        }

        logger.info("   📤 Uploading image with overlay to Cloudinary...")
        upload_result = cloudinary_client.upload_with_transformations(
            image_url=image_url, upload_options=upload_options
        )

        if upload_result.get("secure_url"):
            logger.info(
                f"   ✅ Image uploaded with overlay. URL: {upload_result['secure_url']}"
            )
            return {
                "status": "success",
                "overlaid_url": upload_result["secure_url"],
                "original_url": image_url,
                "overlay_applied": True,
            }
        else:
            logger.warning("Upload failed, trying without overlay")
            # Fallback: upload without overlay
            fallback_result = cloudinary_client.upload(image_url=image_url)
            if fallback_result.get("secure_url"):
                return {
                    "status": "success",
                    "overlaid_url": fallback_result["secure_url"],
                    "original_url": image_url,
                    "overlay_applied": False,
                }
            else:
                return {
                    "status": "error",
                    "message": "Upload failed",
                    "overlaid_url": image_url,
                }

    except Exception as e:
        logger.error(f"Error uploading with overlay: {e}")
        # Fallback: upload without overlay
        try:
            fallback_result = cloudinary_client.upload(image_url=image_url)
            if fallback_result.get("secure_url"):
                return {
                    "status": "success",
                    "overlaid_url": fallback_result["secure_url"],
                    "original_url": image_url,
                    "overlay_applied": False,
                }
        except Exception as fallback_error:
            logger.error(f"Fallback upload also failed: {fallback_error}")

        return {
            "status": "error",
            "message": f"Upload failed: {str(e)}",
            "overlaid_url": image_url,
        }


apply_overlay_chain = RunnableLambda(_apply_overlay_logic)
