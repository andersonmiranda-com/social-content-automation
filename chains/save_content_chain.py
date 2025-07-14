"""
Chain to save generated content to Google Sheets.
"""

import uuid
from datetime import datetime

from langchain_core.runnables import Runnable, RunnableLambda

from tools.google_sheets_tool import read_from_sheet_chain, upsert_sheet_chain
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _save_content_logic(data: dict) -> dict:
    """
    Orchestrates saving content to Google Sheets.

    This function performs two main actions:
    1.  Updates the 'Topics' sheet to mark the used topic with a 'created' timestamp.
    2.  Appends the generated content for each format (post, reel, carousel)
        to the 'Generated' sheet with an auto-incrementing ID.

    Args:
        data: A dictionary containing topic information at the root level,
              and generated content under the 'content_data' key.

    Returns:
        The original data dictionary, augmented with the status of the save operations.
    """
    logger.info("--- 💾 Saving content to Google Sheets ---")

    # The topic data is at the root of the input dictionary.
    topic_id = data["id_topic"]
    topic_name = data["topic"]
    category = data["category"]

    # The generated content is in a nested dictionary.
    content_data = data["content_data"]

    # 1. Update the 'Topics' sheet
    logger.info(f"   - Updating topic '{topic_name}' in Topics sheet.")
    update_topic_payload = {
        "range_name": "Topics",
        "filter_key": "id_topic",
        "filter_value": topic_id,
        "row_data": {"created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
    }
    upsert_sheet_chain.invoke(update_topic_payload)

    # 2. Add content to the 'Generated' sheet with an auto-incrementing ID
    logger.info("   - Adding generated content to Generated sheet.")

    # Get the last ID from the 'Generated' sheet to auto-increment
    read_payload = {"range_name": "Generated"}
    read_result = read_from_sheet_chain.invoke(read_payload)
    sheet_data = read_result.get("sheet_data", [])

    last_id = 0
    if sheet_data:
        try:
            # Filter for valid, numeric IDs before finding the max
            numeric_ids = [
                int(row["id"])
                for row in sheet_data
                if row.get("id") and row["id"].isdigit()
            ]
            if numeric_ids:
                last_id = max(numeric_ids)
        except (ValueError, KeyError):
            logger.warning(
                "Could not determine last ID from sheet. A new one will be created."
            )
            last_id = 0

    next_id = last_id + 1

    content_types = ["reel", "post", "carousel"]
    for content_type in content_types:
        if content_type in content_data:
            content_item = content_data[content_type]
            row_id = next_id
            logger.info(f"     - Adding {content_type} content with id {row_id}")
            row_data = {
                "id": str(row_id),
                "topic": topic_name,
                "id_topic": topic_id,
                "category": category,
                "type": content_type,
                "content": content_item.get("content"),
                "title": content_item.get("title"),
                "subtitle": content_item.get("subtitle"),
                "caption": content_item.get("caption"),
                "hashtags": content_item.get("hashtags"),
                "image_url": data.get("image_url") if content_type == "post" else "",
            }
            add_content_payload = {
                "range_name": "Generated",
                "filter_key": "id",
                "filter_value": str(row_id),
                "row_data": row_data,
            }
            upsert_sheet_chain.invoke(add_content_payload)
            next_id += 1

    data["save_status"] = "success"
    return data


save_content_chain: Runnable = RunnableLambda(_save_content_logic)
