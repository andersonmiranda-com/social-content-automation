"""
Chain to process data read from a Google Sheet.
It filters for unposted topics, selects one randomly, and prepares it for the next step.
"""

import random

from langchain_core.runnables import RunnableLambda

from utils.logger import setup_logger

logger = setup_logger(__name__)


def _select_topic_logic(data: dict) -> dict:
    """
    Filters the sheet data for rows where 'created' is empty and selects one at random.

    Args:
        data: The input dictionary, expected to contain 'sheet_data'.

    Returns:
        A dictionary representing the randomly selected row.

    Raises:
        ValueError: If no data is read or no unposted topics are found.
    """
    sheet_data = data.get("sheet_data", [])
    if not sheet_data:
        logger.error("No data received from the previous step.")
        raise ValueError("No data read from Google Sheet.")

    # Filter for rows where the 'created' column is empty or does not exist.
    unposted_topics = [row for row in sheet_data if not row.get("created", "").strip()]

    if not unposted_topics:
        logger.warning("No unposted topics found in the Google Sheet.")
        raise ValueError("No unposted topics found to process.")

    # Select a random topic from the filtered list
    selected_row = random.choice(unposted_topics)
    topic_text = selected_row.get("topic")

    if not topic_text:
        available_keys = list(selected_row.keys())
        error_msg = f"Selected row is missing a 'Topic' column or the value is empty. Available columns are: {available_keys}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f"Randomly selected row: {selected_row}")

    return selected_row


select_topic_chain = RunnableLambda(_select_topic_logic)
