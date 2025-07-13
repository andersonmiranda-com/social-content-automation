"""
Fake Google Sheets Tool
- Simulates saving post and image data to a Google Sheet.
"""

import csv
from datetime import datetime
from io import StringIO

from langchain_core.runnables import RunnableLambda

from services.sheets_client import GoogleSheetsClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _save_to_sheet_logic(data: dict) -> dict:
    """
    Receives the full data bag, formats it as a CSV row,
    and returns a success status.
    """

    print(f"--- 📝 Saving to Google Sheets ---")

    # Extract data to save
    post_title = data.get("post_data", {}).get("title", "N/A")
    post_caption = data.get("post_data", {}).get("caption", "N/A")
    # Read the generic, top-level key from the data bag
    image_url = data.get("image_url", "N/A")

    # Simulate creating a CSV row
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Caption", "Image URL"])
    writer.writerow([post_title, post_caption, image_url])

    print(
        f"   ✍️  Row to save: ['{post_title}', '{post_caption[:20]}...', '{image_url}']"
    )

    # Get the CSV string
    csv_string = output.getvalue()
    print(f"   Binary data (first 50 chars): {csv_string[:50].encode('utf-8')}...")

    print("   ✅  Save to Google Sheet successful.")

    return {"sheet_status": "success", "saved_data": csv_string}


def _read_from_sheet_logic(data: dict) -> dict:
    """
    Simulates reading all rows from a Google Sheet.
    """
    print("--- 📥 Reading from Google Sheets ---")

    # In a real implementation, you would connect to the Google Sheets API here.
    # For this simulation, we'll read from a local CSV file.
    client = GoogleSheetsClient()
    sheet_data = client.read_sheet()

    if sheet_data is not None:
        logger.info(f"Read {len(sheet_data)} rows from the sheet.")
        print(f"   ✅ Read {len(sheet_data)} rows from the sheet.")
        return {"sheet_data": sheet_data, "read_status": "success"}
    else:
        logger.error("Failed to read data from Google Sheet.")
        print("   ❌ Failed to read data from Google Sheet.")
        return {
            "sheet_data": [],
            "read_status": "error",
            "error_message": "Failed to read from Google Sheets API.",
        }


def _upsert_sheet_logic(data: dict) -> dict:
    """
    Receives filter criteria and data to upsert into a Google Sheet.
    Expected keys in data: 'filter_key', 'filter_value', 'row_data'.
    """
    print("--- ✍️ Upserting to Google Sheets ---")

    filter_key = data.get("filter_key")
    filter_value = data.get("filter_value")
    row_data = data.get("row_data")

    if not all([filter_key, filter_value, row_data]):
        raise ValueError(
            "Missing 'filter_key', 'filter_value', or 'row_data' in input."
        )

    # Assert to help the linter understand the types are now guaranteed
    assert filter_key is not None
    assert row_data is not None

    client = GoogleSheetsClient()
    result = client.upsert_row(filter_key, str(filter_value), row_data)

    if result:
        print(f"   ✅ Successfully upserted row for '{filter_key}={filter_value}'.")
        data["upsert_status"] = "success"
    else:
        print(f"   ❌ Failed to upsert row for '{filter_key}={filter_value}'.")
        data["upsert_status"] = "failed"

    # Return the original data bag for subsequent steps
    return data


save_to_sheet_chain = RunnableLambda(_save_to_sheet_logic)

read_from_sheet_chain = RunnableLambda(_read_from_sheet_logic)

upsert_sheet_chain = RunnableLambda(_upsert_sheet_logic)
