from typing import Any, Dict, Optional

import cloudinary
import cloudinary.uploader

from utils.config_loader import load_config
from utils.env_loader import load_environment
from utils.logger import setup_logger

load_environment()

logger = setup_logger(__name__)


class CloudinaryClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CloudinaryClient, cls).__new__(cls)
            cls._instance._init_client()
        return cls._instance

    def _init_client(self):
        """Initializes the Cloudinary client with credentials."""
        self.config = load_config("cloudinary")
        cloudinary.config(
            cloud_name=self.config["cloud_name"],
            api_key=self.config["api_key"],
            api_secret=self.config["api_secret"],
        )

    def upload(self, image_url: str, folder: Optional[str] = None) -> Dict[str, Any]:
        """
        Uploads an image to Cloudinary from a given URL.

        Args:
            image_url: The URL of the image to upload.
            folder: The specific folder to upload the image to, overriding the default.

        Returns:
            A dictionary containing the response from Cloudinary.
        """
        try:
            # Use the provided folder or fall back to the default from config
            upload_folder = folder or self.config.get("folder")

            upload_options = {
                "upload_preset": self.config.get("upload_preset"),
                "folder": upload_folder,
            }
            # Filter out None values
            upload_options = {k: v for k, v in upload_options.items() if v is not None}

            logger.info(f"Uploading to Cloudinary folder: '{upload_folder}'")
            result = cloudinary.uploader.upload(
                image_url,
                **upload_options,
            )
            return result
        except Exception as e:
            logger.error(f"Error uploading to Cloudinary: {e}")
            raise

    def upload_with_transformations(
        self, image_url: str, upload_options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Uploads an image to Cloudinary with transformations applied during upload.

        Args:
            image_url: The URL of the image to upload.
            upload_options: Dictionary containing upload options including transformations.

        Returns:
            A dictionary containing the response from Cloudinary.
        """
        try:
            # Use the provided folder or fall back to the default from config
            upload_folder = upload_options.get("folder") or self.config.get("folder")

            # Prepare upload options
            options = {
                "upload_preset": self.config.get("upload_preset"),
                "folder": upload_folder,
            }

            # Add transformations if provided
            if "transformation" in upload_options:
                options["transformation"] = upload_options["transformation"]

            # Filter out None values
            options = {k: v for k, v in options.items() if v is not None}

            logger.info(
                f"Uploading to Cloudinary folder: '{upload_folder}' with transformations"
            )
            result = cloudinary.uploader.upload(
                image_url,
                **options,
            )
            return result
        except Exception as e:
            logger.error(f"Error uploading to Cloudinary with transformations: {e}")
            raise


cloudinary_client = CloudinaryClient()
