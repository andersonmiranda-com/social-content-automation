"""
Main entry point for running the social content publishing pipeline.
"""

import asyncio
import json
from typing import Dict, Any

from pipelines.publish_social_post_pipeline import publish_social_post_pipeline
from utils.logger import setup_logger
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = setup_logger(__name__)


async def main():
    """Runs the main publishing pipeline and prints the result."""
    logger.info("Starting the social post publishing pipeline...")
    initial_input: Dict[str, Any] = {}
    result = await publish_social_post_pipeline.ainvoke(initial_input)
    logger.info("Pipeline finished.")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
