"""
Full social post pipeline with the following sequence:
1. Generate post text.
2. Generate an image based on the post text.
3. Upload the generated image to a cloud service.
4. Save the post text and the final image URL to a spreadsheet.
"""

from operator import itemgetter
from typing import Any, Dict

from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from chains.generate_image import generate_image_chain

# Import all the building blocks (chains)
from chains.generate_post import (
    generate_carousel_chain,
    generate_post_chain,
    generate_reel_chain,
)
from chains.select_topic import select_topic_chain
from chains.upload_chain import upload_chain
from tools.google_sheets_tool import read_from_sheet_chain, save_to_sheet_chain


def _preprocess_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts the 'topic' from the input dictionary.
    Handles both direct calls and LangServe's wrapped input.
    """
    inner_input = data.get("input", data)
    return {"topic": inner_input.get("topic", "No topic provided")}


# The sequential pipeline definition
social_post_pipeline = (
    # Step 1: Read all data from the sheet
    read_from_sheet_chain
    # Step 2: Filter for unposted topics and select one randomly
    | select_topic_chain
    # Step 3: Generate all content types in parallel using the specialized chains.
    | RunnablePassthrough.assign(
        content_data=RunnablePassthrough.assign(
            reel=generate_reel_chain,
            post=generate_post_chain,
            carousel=generate_carousel_chain,
        )
    )
    # The subsequent steps (image generation, upload, save) are commented out
    # as they need to be adapted to handle the new `content_data` structure.
    # For example, you might want to generate one image based on the "post" content.
    #
    # # Step 4: Generate image data from 'post' content, add it as 'image_data'
    # | RunnablePassthrough.assign(
    #     image_data=(
    #         RunnableLambda(lambda x: x["content_data"]["post"])
    #         | generate_image_chain
    #     )
    # )
    # # Step 5: Upload image and assign just the final URL to a new key
    # | RunnablePassthrough.assign(
    #     image_url=(
    #         RunnableLambda(lambda x: x["image_data"])
    #         | upload_chain
    #         | itemgetter("image_url")
    #     )
    # )
    # # Step 6: Pass the whole bag to the final saving step.
    # | save_to_sheet_chain
)
