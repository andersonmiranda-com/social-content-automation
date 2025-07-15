import cloudinary
import cloudinary.uploader
from typing import Dict, Any, Optional
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


cloudinary_client = CloudinaryClient()
