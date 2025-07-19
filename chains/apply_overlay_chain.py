"""
Apply Overlay Chain

This chain applies an overlay to images using Cloudinary.
"""

from typing import Any, Dict

from langchain_core.runnables import RunnableLambda

from tools.cloudinary_tool import apply_overlay_chain as cloudinary_overlay_chain
from utils.logger import setup_logger

logger = setup_logger(__name__)


def apply_overlay_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply overlay watermark to generated image.

    Args:
        data: Dictionary containing:
            - image_data: The generated image data (URL)

    Returns:
        Dictionary with watermarked image data
    """
    try:
        image_data = data.get("image_data", "")

        if not image_data:
            raise ValueError("No image data provided for watermarking")

        logger.info("--- 💧 Applying overlay watermark to image ---")

        # Use the cloudinary tool to apply overlay
        overlay_result = cloudinary_overlay_chain.invoke(
            {
                "image_url": image_data,
                "position": "bottom_right",
                "opacity": 0.7,
            }
        )

        if overlay_result.get("status") == "success":
            logger.info("✅ Overlay applied successfully")
            return {
                "status": "success",
                "original_image": image_data,
                "overlaid_image": overlay_result.get("overlaid_url"),
                "overlay_url": overlay_result.get("overlay_url"),
            }
        else:
            raise Exception(
                f"Overlay application failed: {overlay_result.get('message')}"
            )

    except Exception as e:
        logger.error(f"Error applying overlay: {e}")
        return {
            "status": "error",
            "message": f"Failed to apply overlay: {str(e)}",
            "overlaid_image": image_data,  # Return original image as fallback
        }


# Create the overlay application chain
apply_overlay_chain = RunnableLambda(apply_overlay_logic)
