"""
Telegram Client Service

This module handles Telegram Bot API operations for posting content.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import requests

from utils.config_loader import load_config
from utils.logger import setup_logger

logger = setup_logger(__name__)


class TelegramClient:
    """Service for managing Telegram Bot operations."""

    def __init__(self):
        """Initialize the Telegram client with configuration."""
        self._config = None
        self._bot_token = None
        self._chat_id = None
        self._base_url = None
        self._initialized = False

        logger.info("Telegram client created (lazy initialization)")

    def _initialize(self):
        """Lazy initialization of Telegram client."""
        if self._initialized:
            return

        # Load environment variables
        from dotenv import load_dotenv

        load_dotenv()

        self._config = load_config("telegram")

        # Get bot token from environment or config
        self._bot_token = os.getenv("TELEGRAM_BOT_TOKEN") or self._config.get(
            "bot_token"
        )
        if not self._bot_token:
            raise ValueError("Telegram bot token not found in configuration")

        # Get chat ID from environment or config
        self._chat_id = os.getenv("TELEGRAM_CHAT_ID") or self._config.get("chat_id")
        if not self._chat_id:
            raise ValueError("Telegram chat ID not found in configuration")

        self._base_url = f"https://api.telegram.org/bot{self._bot_token}"
        self._initialized = True

        logger.info("Telegram client initialized successfully")

    @property
    def config(self):
        """Get config with lazy initialization."""
        self._initialize()
        return self._config

    @property
    def bot_token(self):
        """Get bot token with lazy initialization."""
        self._initialize()
        return self._bot_token

    @property
    def chat_id(self):
        """Get chat ID with lazy initialization."""
        self._initialize()
        return self._chat_id

    @property
    def base_url(self):
        """Get base URL with lazy initialization."""
        self._initialize()
        return self._base_url

    def send_message(self, text: str, parse_mode: str = "HTML") -> Dict[str, Any]:
        """
        Send a text message to the configured chat.

        Args:
            text: Message text to send
            parse_mode: Text parsing mode (HTML, Markdown, etc.)

        Returns:
            API response from Telegram
        """
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode}

            logger.info("Sending message to Telegram...")
            response = requests.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info("✅ Message sent successfully to Telegram")
                return result
            else:
                raise Exception(f"Telegram API error: {result.get('description')}")

        except Exception as e:
            logger.error(f"Error sending message to Telegram: {e}")
            raise

    def send_photo(
        self,
        photo: Union[str, Path],
        caption: Optional[str] = None,
        parse_mode: str = "HTML",
    ) -> Dict[str, Any]:
        """
        Send a photo with optional caption to the configured chat.

        Args:
            photo: Photo file path or URL
            caption: Optional caption text
            parse_mode: Text parsing mode for caption

        Returns:
            API response from Telegram
        """
        try:
            url = f"{self.base_url}/sendPhoto"

            # Prepare the payload
            payload = {"chat_id": self.chat_id, "parse_mode": parse_mode}

            if caption:
                payload["caption"] = caption

            # Handle file upload or URL
            if isinstance(photo, (str, Path)) and Path(photo).exists():
                # Local file
                with open(photo, "rb") as photo_file:
                    files = {"photo": photo_file}
                    logger.info(f"Sending local photo: {photo}")
                    response = requests.post(url, data=payload, files=files)
            else:
                # URL
                payload["photo"] = str(photo)
                logger.info(f"Sending photo from URL: {photo}")
                response = requests.post(url, json=payload)

            response.raise_for_status()
            result = response.json()

            if result.get("ok"):
                logger.info("✅ Photo sent successfully to Telegram")
                return result
            else:
                raise Exception(f"Telegram API error: {result.get('description')}")

        except Exception as e:
            logger.error(f"Error sending photo to Telegram: {e}")
            raise

    def send_media_group(
        self, media: list, caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a group of media files to the configured chat.

        Args:
            media: List of media items (photos, videos, etc.)
            caption: Optional caption for the media group

        Returns:
            API response from Telegram
        """
        try:
            url = f"{self.base_url}/sendMediaGroup"

            payload = {"chat_id": self.chat_id, "media": media}

            if caption:
                payload["caption"] = caption

            logger.info("Sending media group to Telegram...")
            response = requests.post(url, json=payload)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                logger.info("✅ Media group sent successfully to Telegram")
                return result
            else:
                raise Exception(f"Telegram API error: {result.get('description')}")

        except Exception as e:
            logger.error(f"Error sending media group to Telegram: {e}")
            raise

    def get_bot_info(self) -> Dict[str, Any]:
        """
        Get information about the bot.

        Returns:
            Bot information from Telegram API
        """
        try:
            url = f"{self.base_url}/getMe"
            response = requests.get(url)
            response.raise_for_status()

            result = response.json()
            if result.get("ok"):
                bot_info = result.get("result", {})
                logger.info(
                    f"Bot info: {bot_info.get('first_name')} (@{bot_info.get('username')})"
                )
                return bot_info
            else:
                raise Exception(f"Telegram API error: {result.get('description')}")

        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test the connection to Telegram API.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            self.get_bot_info()
            logger.info("✅ Telegram connection test successful")
            return True
        except Exception as e:
            logger.error(f"❌ Telegram connection test failed: {e}")
            return False


# Singleton instance
telegram_client = TelegramClient()
