import os
import openai
from typing import TypedDict


from common.llm_communicator import LLMCommunicator
from common.response_generator import ResponseGenerator


class GptConfig(TypedDict):
    api_url: str
    generate_path: str
    model: str
    embed_path: str
    temperature: float
    max_tokens: int

class GptCommunicator(LLMCommunicator):
    """A singleton class to communicate with the LLM API."""
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # If no instance exists, create a new one using the parent's __new__
            cls._instance = super().__new__(cls)
        return cls._instance  # Return the existing instance

    def __init__(self, config: GptConfig=None):
        if config is not None:
            self.change_config(config)
    
    def change_config(self, config: GptConfig):
        """
        Set the configuration for the LLMCommunicator.
        
        Args:
            generate_url: URL for generating responses
            model: Model name to use
            embed_url: URL for embedding requests
        """
        self.model_name = config["model"]
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 150)
        
        api_key = os.environ.get("GPT_API_KEY")
        openai.api_key = api_key
        
        self.response_generator = ResponseGenerator(self)
        return super().change_config(config)

    def send_gen_request(self, prompt):
        try:
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            print(f"Response: {response}")
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {e}"

        
