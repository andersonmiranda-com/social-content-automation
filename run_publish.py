"""
Script to execute the social post publishing pipeline.

This script initializes and runs the main pipeline to publish content
to social media, and prints the final output.
"""

import asyncio
from dotenv import load_dotenv

from pipelines.publish_social_post_pipeline import publish_social_post_pipeline
from utils.logger import setup_logger

# Load environment variables from .env file
load_dotenv()

logger = setup_logger(__name__)


def main():
    """
    Main function to run the social post pipeline.
    """
    logger.info("Starting the social post publishing pipeline...")

    # The input to the first chain is an empty dict for now
    initial_input = {}

    # Using asyncio.run for async compatibility if any chain is async
    result = asyncio.run(publish_social_post_pipeline.ainvoke(initial_input))

    logger.info("Pipeline execution finished.")
    logger.info("Final output:")
    logger.info(result)


if __name__ == "__main__":
    main()
