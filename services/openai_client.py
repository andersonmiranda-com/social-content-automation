from langchain_openai import ChatOpenAI
from openai import OpenAI
from typing import Literal


class OpenAIClient:
    def __init__(self, temperature=0.7, model="gpt-3.5-turbo"):
        """
        Initialize the OpenAIClient.

        Args:
            temperature (float, optional): The temperature for the model. Defaults to 0.7.
            model (str, optional): The model to use. Defaults to 'gpt-3.5-turbo'.
        """
        self.chat_llm = ChatOpenAI(temperature=temperature, model=model)
        self.client = OpenAI()

    def invoke(self, prompt: str) -> str:
        response = self.chat_llm.invoke(prompt)
        return str(response.content)

    def generate_image(
        self,
        prompt: str,
        model: str,
        response_format: Literal["url", "b64_json"] | None = None,
        quality: Literal["standard", "hd"] | None = None,
        style: Literal["vivid", "natural"] | None = None,
    ) -> str:
        """
        Generates an image using DALL-E.

        Args:
            prompt: The text prompt for the image.
            model: The DALL-E model to use.
            response_format: The format of the generated image.
            quality: The quality of the generated image.
            style: The style of the generated image.


        Returns:
            The URL or b64_json of the generated image.
        """
        request_params = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
        }
        if response_format:
            request_params["response_format"] = response_format
        if quality:
            request_params["quality"] = quality
        if style:
            request_params["style"] = style

        response = self.client.images.generate(**request_params)

        if not response.data:
            raise ValueError("Image generation failed, no data returned.")

        image_data = response.data[0]
        if image_data.url:
            return image_data.url
        elif image_data.b64_json:
            return image_data.b64_json
        else:
            raise ValueError("Image generation failed, no URL or b64_json returned.")
