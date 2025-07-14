"""
Generate Content Chains

This module creates specialized chains for generating different types of content
(e.g., REEL, POST, CAROUSEL) based on dedicated prompts.
"""

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI

from utils.config_loader import load_config
from utils.file_utils import load_prompt_template

# ----------------------------------------------------------------------------
# 1. Load Configuration and System Prompt
# ----------------------------------------------------------------------------
config = load_config("generate_post")
SYSTEM_PROMPT_PATH = config.get("system_prompt_template")
USER_PROMPTS_PATHS = config.get("user_prompts", {})

if not SYSTEM_PROMPT_PATH or not USER_PROMPTS_PATHS:
    raise ValueError(
        "Config file must contain 'system_prompt_template' and a 'user_prompts' dictionary."
    )

try:
    SYSTEM_PROMPT_TEMPLATE = load_prompt_template(SYSTEM_PROMPT_PATH)
except FileNotFoundError as e:
    raise RuntimeError(f"Could not find system prompt file: {e}") from e


# ----------------------------------------------------------------------------
# 2. Factory Function for Content Generation Chains
# ----------------------------------------------------------------------------
def create_content_chain(user_prompt_path: str) -> Runnable:
    """
    Factory function to create a content generation chain.
    Args:
        user_prompt_path: The path to the user-specific prompt template.
    Returns:
        A runnable chain for content generation.
    """
    try:
        user_prompt_template = load_prompt_template(user_prompt_path)
    except FileNotFoundError as e:
        raise RuntimeError(f"Could not find user prompt file: {e}") from e

    llm = ChatOpenAI(
        model=config["model"],
        temperature=config.get("temperature", 0.7),
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_TEMPLATE),
            ("user", user_prompt_template),
        ]
    )

    return prompt | llm | JsonOutputParser()


# ----------------------------------------------------------------------------
# 3. Instantiate and Export Chains
# ----------------------------------------------------------------------------
# Create a specific chain for each content type defined in the config.
generate_reel_chain = create_content_chain(USER_PROMPTS_PATHS["reel"])
generate_post_chain = create_content_chain(USER_PROMPTS_PATHS["post"])
generate_carousel_chain = create_content_chain(USER_PROMPTS_PATHS["carousel"])
