"""
Fake Google Sheets Tool
- Simulates saving post and image data to a Google Sheet.
"""

import csv
from io import StringIO

from langchain_core.runnables import RunnableLambda

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
    final_image_url = data.get("final_image_url", "N/A")

    # Simulate creating a CSV row
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Caption", "Image URL"])
    writer.writerow([post_title, post_caption, final_image_url])

    print(
        f"   ✍️  Row to save: ['{post_title}', '{post_caption[:20]}...', '{final_image_url}']"
    )

    # Get the CSV string
    csv_string = output.getvalue()
    print(f"   Binary data (first 50 chars): {csv_string[:50].encode('utf-8')}...")

    print("   ✅  Save to Google Sheet successful.")

    return {"sheet_status": "success", "saved_data": csv_string}


save_to_sheet_chain = RunnableLambda(_save_to_sheet_logic)
