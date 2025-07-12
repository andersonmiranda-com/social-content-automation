import os
from typing import Optional

from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient


def get_llm_client(model: Optional[str] = None):
    """
    Return an LLM client instance for the selected provider, optionally using a specific model.

    Args:
        model (str, optional): The model to use. If None, uses the default for the provider.

    Returns:
        An instance of the selected LLM client.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "openai":
        return OpenAIClient(model=model) if model else OpenAIClient()
    elif provider == "anthropic":
        return AnthropicClient(model=model) if model else AnthropicClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
