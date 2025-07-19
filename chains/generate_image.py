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
        post_data: A dictionary containing:
            - content: The post content to generate image for
            - model: Optional model override (e.g., "dall-e-3")
            - quality: Optional quality setting for DALL-E 3
            - style: Optional style setting for DALL-E 3

    Returns:
        A dictionary containing the URL of the generated image.
    """
    # Load default config but allow overrides from post_data
    config = load_config("generate_image")

    # Override config with any parameters passed in post_data
    model = post_data.get("model", config["model"])
    quality = post_data.get("quality", config.get("quality", "standard"))
    style = post_data.get("style", config.get("style", "vivid"))

    prompt_template_str = load_prompt_template("prompts/image_prompt.txt")
    prompt_template = PromptTemplate.from_template(prompt_template_str)

    llm_client = OpenAIClient()

    formatted_prompt = prompt_template.format(content=post_data.get("content", ""))

    logger.info(f"--- 🎨 Generating image with {model} ---")
    logger.debug(f"Formatted prompt: {formatted_prompt}")

    image_generation_params = {
        "prompt": formatted_prompt,
        "model": model,
    }

    # Add parameters only supported by DALL-E 3
    if model == "dall-e-3":
        image_generation_params["quality"] = quality
        image_generation_params["style"] = style

    if "response_format" in config:
        image_generation_params["response_format"] = config["response_format"]

    image_data = llm_client.generate_image(**image_generation_params)

    logger.info(f"   ✅ Image generated: {image_data}")

    return {"image_data": image_data}


generate_image_chain = RunnableLambda(generate_image_logic)
