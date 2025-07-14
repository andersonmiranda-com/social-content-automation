"""
This is an example of how to run the full social post pipeline.
This script is the "entry point" that triggers the execution.
"""

import os

from dotenv import load_dotenv
from utils.logger import setup_logger

# Load environment variables from .env file
# Make sure you have your OPENAI_API_KEY set in a .env file
load_dotenv()

# Setup logger
logger = setup_logger(__name__)

# We need to check if the API key is set, otherwise, the LLM will fail.
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY environment variable not set.")
    logger.error("Please create a .env file and add your OpenAI API key to it.")
else:
    # Import the pipeline we built
    from pipelines.social_post_pipeline import social_post_pipeline

    logger.info("--- Starting Pipeline ---")
    logger.info(
        "The pipeline will now read from the sheet and select a topic on its own."
    )
    logger.info("-" * 20)

    # HERE IS THE INVOKE CALL
    # We call .invoke() on the fully constructed pipeline object
    # An empty dictionary is passed as input because the pipeline is self-sufficient
    final_result = social_post_pipeline.invoke({})

    logger.info("-" * 20)
    logger.info("--- Pipeline Finished ---")
    logger.info("Final Result:")
    logger.info(final_result)
