"""
Chain for publishing content to LinkedIn.
"""

from langchain_core.runnables import RunnableLambda
from services.linkedin_client import LinkedInClient
from utils.logger import setup_logger

# Setting up the logger for this module
logger = setup_logger(__name__)


def publish_linkedin_post(input_data: dict) -> dict:
    """
    Initializes a LinkedIn client and publishes a post with an image.

    Args:
        input_data: A dictionary containing 'content', 'hashtags', and 'image_url'.

    Returns:
        A dictionary with the response from the LinkedIn API.
    """
    logger.info("Starting LinkedIn publishing chain.")

    # Extract data from input
    content = input_data.get("content")
    hashtags = input_data.get("hashtags")
    image_url = input_data.get("image_url")  # [[memory:3066873]]

    if not all([content, hashtags, image_url]):
        error_msg = "Missing required fields in input data. Need 'content', 'hashtags', and 'image_url'."
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Prepare the post text
    post_text = f"{content}\n\n{hashtags}"

    assert image_url is not None, "image_url should not be None here"

    try:
        # Initialize the client
        linkedin_client = LinkedInClient()

        # Publish the post
        logger.info(f"Publishing to LinkedIn with image: {image_url}")
        result = linkedin_client.publish_post_with_image(
            text=post_text, image_url=image_url
        )

        logger.info("Successfully published post to LinkedIn.")
        return {"linkedin_post_id": result.get("id"), "status": "published"}

    except Exception as e:
        logger.error(f"Failed to publish post to LinkedIn: {e}")
        # Re-raise the exception to be handled by the pipeline
        raise


# Creating the RunnableLambda for the chain
linkedin_post_chain = RunnableLambda(publish_linkedin_post)
