from langchain_anthropic import ChatAnthropic

from .base_client import LLMClient


class AnthropicClient(LLMClient):
    def __init__(self, temperature=0.7, model="claude-3-opus-20240229"):
        """
        Initialize the AnthropicClient.

        Args:
            temperature (float, optional): The temperature for the model. Defaults to 0.7.
            model (str, optional): The model to use. Defaults to 'claude-3-opus-20240229'.
        """
        self.llm = ChatAnthropic(
            temperature=temperature, model_name=model, timeout=None, stop=[]
        )

    def invoke(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)
        return str(response.content)
