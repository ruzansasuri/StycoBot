from typing import Dict
from abc import ABC, abstractmethod


class LLMCommunicator(ABC):
    def __init__(self, generate_url: str, model: str, embed_url: str):
        """
        Initialize the LLMCommunicator with the given configuration.
        
        Args:
            generate_url: URL for generating responses
            model: Model name to use
            embed_url: URL for embedding requests
        """
        self.set_config(generate_url, model, embed_url)
    
    @abstractmethod
    def change_config(self, config: Dict) -> None   :
        pass
    
    @abstractmethod
    def send_gen_request(self, prompt: str) -> str:
        pass
    
    # @abstractmethod
    # def send_embed_request(self, prompt: str) -> str:
    #     pass