"""
Generate Image Chain
"""

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

from services.openai_client import OpenAIClient
from utils.config_loader import load_config
from utils.file_utils import load_prompt_template
from utils.logger import setup_logger

logger = setup_logger(__name__)


def generate_image_logic(post_data: dict) -> dict:
    """
    Generates an image based on post content using an LLM.

    Args:
        post_data: A dictionary containing the post content under the 'content' key.

    Returns:
        A dictionary containing the URL of the generated image.
    """
    config = load_config("generate_image")
    prompt_template_str = load_prompt_template("prompts/image_prompt.txt")
    prompt_template = PromptTemplate.from_template(prompt_template_str)

    llm_client = OpenAIClient()

    formatted_prompt = prompt_template.format(content=post_data.get("content", ""))

    logger.info("--- 🎨 Generating image with prompt ---")
    logger.debug(f"Formatted prompt: {formatted_prompt}")

    image_generation_params = {
        "prompt": formatted_prompt,
        "model": config["model"],
    }

    # Add parameters only supported by DALL-E 3
    if config["model"] == "dall-e-3":
        image_generation_params["quality"] = config.get("quality", "standard")
        image_generation_params["style"] = config.get("style", "vivid")

    if "response_format" in config:
        image_generation_params["response_format"] = config["response_format"]

    image_data = llm_client.generate_image(**image_generation_params)

    logger.info(f"   ✅ Image generated: {image_data}")

    return {"image_data": image_data}


generate_image_chain = RunnableLambda(generate_image_logic)
