"""
This script is used to manually trigger the Canva OAuth2 flow
and print the refresh token to the console.
"""

import os
from services.canva_client import CanvaClient
from utils.logger import setup_logger

logger = setup_logger(__name__)

if __name__ == "__main__":
    logger.info("Attempting to initialize Canva client to get a new refresh token...")
    try:
        # Temporarily remove the env var to force a new auth flow,
        # bypassing any existing (and potentially invalid) refresh token.
        if "CANVA_REFRESH_TOKEN" in os.environ:
            logger.warning(
                "Temporarily ignoring existing CANVA_REFRESH_TOKEN to force new login."
            )
            del os.environ["CANVA_REFRESH_TOKEN"]

        # This will now automatically trigger the browser-based auth flow
        client = CanvaClient()

        # The token is saved to canva_token.json by the client's __init__ method.
        # We can also access it from the session object if needed.
        if client.session.token and "refresh_token" in client.session.token:
            refresh_token = client.session.token["refresh_token"]
            logger.info("✅ Canva authorization successful.")
            logger.info("✅ New Canva Refresh Token:")
            print(f"\n{refresh_token}\n")
            logger.info(
                "Please copy the token above and update the CANVA_REFRESH_TOKEN "
                "variable in your .env file."
            )
        else:
            logger.error("Could not retrieve refresh token after authorization.")

    except Exception as e:
        logger.error(f"An error occurred during the Canva authentication process: {e}")
