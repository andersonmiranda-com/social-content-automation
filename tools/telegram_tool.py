"""
Telegram Tool

This module provides LangChain-compatible tools for Telegram operations.
"""

from typing import Any, Dict

from langchain_core.runnables import RunnableLambda

from services.telegram_client import telegram_client
from utils.logger import setup_logger

logger = setup_logger(__name__)


def send_telegram_message_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a message to Telegram.

    Args:
        data: Dictionary containing:
            - text: Message text to send
            - parse_mode: Optional parse mode (default: HTML)

    Returns:
        Dictionary with operation result
    """
    try:
        text = data.get("text")
        parse_mode = data.get("parse_mode", "HTML")

        if not text:
            raise ValueError("No text provided for Telegram message")

        logger.info("--- 📱 Sending message to Telegram ---")

        result = telegram_client.send_message(text=text, parse_mode=parse_mode)

        return {
            "status": "success",
            "message": "Message sent successfully to Telegram",
            "telegram_response": result,
        }

    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return {
            "status": "error",
            "message": f"Failed to send Telegram message: {str(e)}",
        }


def send_telegram_photo_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a photo with caption to Telegram.

    Args:
        data: Dictionary containing:
            - photo_url: URL or path to photo
            - caption: Optional caption text
            - parse_mode: Optional parse mode (default: HTML)

    Returns:
        Dictionary with operation result
    """
    try:
        photo_url = data.get("photo_url")
        caption = data.get("caption")
        parse_mode = data.get("parse_mode", "HTML")

        if not photo_url:
            raise ValueError("No photo URL provided for Telegram photo")

        logger.info("--- 📸 Sending photo to Telegram ---")

        result = telegram_client.send_photo(
            photo=photo_url, caption=caption, parse_mode=parse_mode
        )

        return {
            "status": "success",
            "message": "Photo sent successfully to Telegram",
            "telegram_response": result,
        }

    except Exception as e:
        logger.error(f"Error sending Telegram photo: {e}")
        return {
            "status": "error",
            "message": f"Failed to send Telegram photo: {str(e)}",
        }


def test_telegram_connection_logic(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Test Telegram connection.

    Args:
        data: Empty dictionary (not used)

    Returns:
        Dictionary with connection test result
    """
    try:
        logger.info("--- 🔗 Testing Telegram connection ---")

        success = telegram_client.test_connection()

        if success:
            return {
                "status": "success",
                "message": "Telegram connection test successful",
            }
        else:
            return {"status": "error", "message": "Telegram connection test failed"}

    except Exception as e:
        logger.error(f"Error testing Telegram connection: {e}")
        return {
            "status": "error",
            "message": f"Telegram connection test error: {str(e)}",
        }


# Create LangChain-compatible chains
send_telegram_message_chain = RunnableLambda(send_telegram_message_logic)
send_telegram_photo_chain = RunnableLambda(send_telegram_photo_logic)
test_telegram_connection_chain = RunnableLambda(test_telegram_connection_logic)
