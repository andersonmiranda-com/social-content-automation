"""
Chain for fetching content from Google Sheets.

This chain is responsible for:
1. Connecting to the Google Sheets API.
2. Reading the available posts that are ready to be published.
3. Filtering out already published posts.
4. Selecting one post randomly to be published.
"""

import random
from typing import Dict, List, Any

from langchain.schema.runnable import RunnableLambda

from services.sheets_client import GoogleSheetsClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_content_to_publish(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetches content from Google Sheets, filters for posts ready to be published,
    and selects one at random.

    Args:
        input_data: A dictionary containing the input. Currently unused,
                    as the client handles its own config.

    Returns:
        A dictionary representing the selected post's data.
    """
    logger.info("Starting content selection process...")
    client = GoogleSheetsClient()

    # From n8n workflow, the sheet is 'Generated'
    all_posts = client.read_sheet(range_name="Generated")

    if not all_posts:
        logger.warning("No posts found in the 'Generated' sheet.")
        return {}

    # Filter posts based on n8n workflow criteria
    ready_to_publish = [
        post
        for post in all_posts
        if post.get("type") == "POST"
        and post.get("edited") == "x"
        and not post.get("published")
        and post.get("image_url")
        and not post.get("image_ready_url")
    ]

    if not ready_to_publish:
        logger.info("No posts are ready to be published at this time.")
        return {}

    logger.info(f"Found {len(ready_to_publish)} posts ready to be published.")

    # Select one random post
    selected_post = random.choice(ready_to_publish)
    logger.info(f"Selected post with ID: {selected_post.get('id')}")
    return selected_post


get_content_chain = RunnableLambda(get_content_to_publish)
