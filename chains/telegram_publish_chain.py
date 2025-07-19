"""
Telegram Publish Chain

This chain publishes generated content to Telegram with proper formatting.
"""

from typing import Any, Dict

from langchain_core.runnables import RunnableLambda

from tools.telegram_tool import send_telegram_message_chain, send_telegram_photo_chain
from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def format_telegram_content_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format content for Telegram publication.

    Args:
        data: Dictionary containing:
            - generated_content: Main content text
            - quote: Motivational quote
            - topic: Selected topic

    Returns:
        Dictionary with formatted content
    """
    try:
        generated_content = data.get("generated_content", "")
        quote = data.get("quote", "")
        topic = data.get("topic", "")

        if not generated_content:
            raise ValueError("No content provided for Telegram publication")

        logger.info("--- 📱 Formatting content for Telegram ---")

        # Load Telegram configuration
        config = load_config("telegram")
        enable_hashtags = config.get("enable_hashtags", True)
        default_hashtags = config.get("default_hashtags", [])
        auto_add_hashtags = config.get("auto_add_hashtags", True)

        # Format the message with HTML formatting
        formatted_message = f"<b>{topic}</b>\n\n{generated_content}\n\n<i>{quote}</i>"

        logger.info("✅ Content formatted successfully")

        return {
            "status": "success",
            "formatted_message": formatted_message,
            "original_content": generated_content,
            "quote": quote,
            "topic": topic,
        }

    except Exception as e:
        logger.error(f"Error formatting content for Telegram: {e}")
        return {
            "status": "error",
            "message": f"Failed to format content: {str(e)}",
            "formatted_message": "",
        }


def publish_to_telegram_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Publish formatted content and image to Telegram.

    Args:
        data: Dictionary containing formatted content and image data

    Returns:
        Dictionary with publication result
    """
    try:
        formatted_message = data.get("formatted_message", "")
        image_url = data.get("image_url", "")

        if not formatted_message:
            raise ValueError("No formatted message to publish")

        logger.info("--- 📤 Publishing to Telegram ---")

        # If we have an image, send photo with caption
        if image_url:
            logger.info("📸 Sending photo with caption to Telegram")
            telegram_result = send_telegram_photo_chain.invoke(
                {
                    "photo_url": image_url,
                    "caption": formatted_message,
                    "parse_mode": "HTML",
                }
            )
        else:
            # Fallback to text-only message
            logger.info("📝 Sending text-only message to Telegram")
            telegram_result = send_telegram_message_chain.invoke(
                {"text": formatted_message, "parse_mode": "HTML"}
            )

        if telegram_result.get("status") == "success":
            logger.info("✅ Content and image published successfully to Telegram")
            return {
                "status": "success",
                "message": "Content and image published successfully to Telegram",
                "telegram_response": telegram_result.get("telegram_response"),
                "published_content": formatted_message,
                "published_image": image_url,
            }
        else:
            raise Exception(
                f"Telegram publication failed: {telegram_result.get('message')}"
            )

    except Exception as e:
        logger.error(f"Error publishing to Telegram: {e}")
        return {
            "status": "error",
            "message": f"Failed to publish to Telegram: {str(e)}",
        }


# Create the chains
format_telegram_content_chain = RunnableLambda(format_telegram_content_logic)
publish_to_telegram_chain = RunnableLambda(publish_to_telegram_logic)
