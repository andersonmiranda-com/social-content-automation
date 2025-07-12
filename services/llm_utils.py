from typing import Optional

from services.llm_factory import get_llm_client


def prompt_llm(prompt: str, model: Optional[str] = None, **kwargs) -> str:
    """
    Send a prompt to the selected LLM and return the response as a string.

    Args:
        prompt (str): The prompt to send to the LLM.
        model (str, optional): The model to use. If None, uses the default from the client.
        **kwargs: Additional keyword arguments for the LLM client (if supported).

    Returns:
        str: The response from the LLM as a string.
    """
    llm_client = get_llm_client(model=model)
    response = llm_client.invoke(prompt)
    return response
