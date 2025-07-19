"""
Generate DALL-E-3 Image Chain

This chain generates images using DALL-E-3 model specifically for the RAG content pipeline.
"""

from typing import Any, Dict

from langchain_core.runnables import RunnableLambda

from chains.generate_image import generate_image_chain
from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_dalle_image_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate image using DALL-E-3 model for RAG content.

    Args:
        data: Dictionary containing:
            - generated_content: The generated content text
            - topic: The selected topic

    Returns:
        Dictionary with generated image data
    """
    try:
        generated_content = data.get("generated_content", "")
        topic = data.get("topic", "")

        if not generated_content:
            raise ValueError("No content provided for image generation")

        logger.info("--- 🎨 Generating DALL-E-3 image for RAG content ---")

        # Prepare content for image generation
        image_content = f"Topic: {topic}\n\nContent: {generated_content}"

        # Call the base generate_image chain with DALL-E-3 parameters
        image_result = generate_image_chain.invoke(
            {
                "content": image_content,
                "model": "dall-e-3",
                "quality": "hd",
                "style": "vivid",
            }
        )

        if image_result.get("image_data"):
            logger.info("✅ DALL-E-3 image generated successfully")
            return {
                "status": "success",
                "image_data": image_result["image_data"],
                "model_used": "dall-e-3",
            }
        else:
            raise Exception("No image data returned from generation")

    except Exception as e:
        logger.error(f"Error generating DALL-E-3 image: {e}")
        return {
            "status": "error",
            "message": f"Failed to generate image: {str(e)}",
            "image_data": None,
        }


# Create the DALL-E-3 image generation chain
generate_dalle_image_chain = RunnableLambda(generate_dalle_image_logic)
