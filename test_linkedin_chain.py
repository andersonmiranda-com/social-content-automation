"""
Test script for the LinkedIn publishing chain.

This script allows for isolated testing of the LinkedIn publishing functionality
by invoking the chain with mocked input data. This avoids running the full,
slower pipeline involving Canva and Cloudinary.

Usage:
    pipenv run python test_linkedin_chain.py
"""

import asyncio
from dotenv import load_dotenv

from chains.publish_linkedin_post import linkedin_post_chain
from utils.logger import setup_logger

# Load environment variables from .env file
load_dotenv()

logger = setup_logger(__name__)


async def main():
    """
    Main function to run the isolated LinkedIn publishing chain test.
    """
    logger.info("--- 🚀 Starting isolated LinkedIn chain test ---")

    # Mock input that would normally come from previous pipeline steps
    mock_input = {
        "content": "This is a test post from the isolated test script. 🚀",
        "hashtags": "#testing #automation #python",
        "image_url": "https://res.cloudinary.com/dlvxgjflw/image/upload/v1752590411/social_published/mgga0gxo0x7xiixcdxmw.png",
    }

    logger.info(f"Mock Input: {mock_input}")

    try:
        # Invoke the chain directly with the mock data
        result = await linkedin_post_chain.ainvoke(mock_input)
        logger.info("--- ✅ LinkedIn chain test completed successfully! ---")
        logger.info(f"Result: {result}")

    except Exception as e:
        logger.error(f"--- ❌ LinkedIn chain test failed ---")
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
