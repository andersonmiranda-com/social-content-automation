import os
from .llm_openai import OpenAIClient
from .llm_claude import ClaudeClient


def get_llm_client(model: str = None):
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
    elif provider == "claude":
        return ClaudeClient(model=model) if model else ClaudeClient()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
