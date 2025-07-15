"""
This script guides the user through the OAuth 2.0 authentication process
for the LinkedIn API to obtain a refresh token.
"""

import logging
import os
from services.linkedin_client import LinkedInClient
from utils.logger import setup_logger

# Set OAUTHLIB_INSECURE_TRANSPORT to allow HTTP for local development
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

logger = setup_logger(__name__)

if __name__ == "__main__":
    logger.info("Attempting to initialize LinkedIn client to get auth token...")
    try:
        # 1. Make sure to fill in your credentials in `configs/linkedin.yaml`
        #    or set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET as environment variables.
        client = LinkedInClient()

        # 2. Call a method to trigger authentication
        profile = client.get_user_profile()

        logger.info("Successfully authenticated with LinkedIn.")
        logger.info(f"User Profile ID: {profile.get('id')}")
        logger.info(
            f"User Name: {profile.get('localizedFirstName')} {profile.get('localizedLastName')}"
        )
        logger.info("✅ `linkedin_token.json` has been created successfully.")

    except Exception as e:
        logger.error(f"An error occurred during the authentication process: {e}")
        logger.error(
            "Please ensure your client_id and client_secret are correct and that the redirect URI "
            "in your LinkedIn App settings is set to http://localhost:8080/callback"
        )
