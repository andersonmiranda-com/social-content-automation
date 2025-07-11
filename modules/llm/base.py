class LLMClient:
    def invoke(self, prompt: str) -> str:
        raise NotImplementedError("You must implement this method in the subclass.")
