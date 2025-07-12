"""
Generate Post Chain
"""

import json

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

from utils.config_loader import load_config
from utils.file_utils import load_prompt_template
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_llm(config: dict):
    """Initializes and returns the LLM based on the config."""
    # This can be expanded to use a factory for different models
    return ChatOpenAI(
        model=config["model"],
        temperature=config.get("temperature"),  # Temperature is often optional
    )


def parse_output(text: str) -> dict:
    """Parses the LLM string output into a dictionary."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM output as JSON.")
        return {"error": "Failed to parse JSON response", "raw_output": text}


# Load configuration for the chain
config = load_config("generate_post")

# Validate required configuration
required_keys = ["model", "prompt_template"]
for key in required_keys:
    if key not in config:
        raise ValueError(
            f"Missing required configuration key: '{key}' in generate_text.yaml"
        )

# Load prompt from file specified in config
prompt_template_str = load_prompt_template(config["prompt_template"])
prompt = PromptTemplate.from_template(prompt_template_str)

# Initialize the language model
llm = get_llm(config)

# Define the runnable chain
generate_post_chain = (
    RunnablePassthrough()
    | prompt
    | llm
    | RunnableLambda(lambda x: x.content)
    | RunnableLambda(parse_output)
)
