from langchain_anthropic import ChatAnthropic
from .base import LLMClient


class ClaudeClient(LLMClient):
    def __init__(self, temperature=0.7, model="claude-3-opus-20240229"):
        """
        Initialize the ClaudeClient.

        Args:
            temperature (float, optional): The temperature for the model. Defaults to 0.7.
            model (str, optional): The model to use. Defaults to 'claude-3-opus-20240229'.
        """
        self.llm = ChatAnthropic(temperature=temperature, model=model)

    def invoke(self, prompt: str) -> str:
        return self.llm.invoke(prompt)
