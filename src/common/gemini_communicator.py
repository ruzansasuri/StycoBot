import google.generativeai as genai
import os
from typing import TypedDict

from common.llm_communicator import LLMCommunicator
from common.response_generator import ResponseGenerator


class GeminiConfig(TypedDict):
    api_url: str
    generate_path: str
    model: str
    embed_path: str

class GeminiCommunicator(LLMCommunicator):
    """A singleton class to communicate with the LLM API."""
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # If no instance exists, create a new one using the parent's __new__
            cls._instance = super().__new__(cls)
        return cls._instance  # Return the existing instance

    def __init__(self, config: GeminiConfig=None):
        if config is not None:
            self.change_config(config)
    
    def change_config(self, config: GeminiConfig):
        """
        Set the configuration for the LLMCommunicator.
        
        Args:
            generate_url: URL for generating responses
            model: Model name to use
            embed_url: URL for embedding requests
        """
        self.model_name = config["model"]
        
        api_key = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=api_key)
        
        self.model = genai.GenerativeModel(self.model_name)
        self.response_generator = ResponseGenerator(self)
        return super().change_config(config)

    def send_gen_request(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
