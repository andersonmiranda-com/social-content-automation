from langchain_openai import ChatOpenAI
from .llm_base import LLMClient


class OpenAIClient(LLMClient):
    def __init__(self, temperature=0.7, model="gpt-3.5-turbo"):
        """
        Initialize the OpenAIClient.

        Args:
            temperature (float, optional): The temperature for the model. Defaults to 0.7.
            model (str, optional): The model to use. Defaults to 'gpt-3.5-turbo'.
        """
        self.llm = ChatOpenAI(temperature=temperature, model=model)

    def invoke(self, prompt: str) -> str:
        return self.llm.invoke(prompt)
