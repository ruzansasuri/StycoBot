import requests
from typing import TypedDict

class LlamaCommunicator:
    

    def __init__(self, config_file: str):
        self._change_config(config_file)

    def _change_config(self, config_file):
        """
        Change the configuration of the LLMCommunicator.
        
        Args:
            configs: New configuration dictionary with keys 'api_url',
        """
        self.api_url = configs["api_url"]
        self.generate_path = configs["generate_path"]
        self.model = configs["model"]

    
    def send_request(self, prompt: str) -> str:
        try:
            url = f"{self.api_url}{self.generate_path}"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7,  # Slightly creative for natural language
                "max_tokens": 400
            }
            
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                return f"I found some information but had trouble formatting the response. Please try again."
                
        except requests.exceptions.RequestException as e:
            return f"I found some information but couldn't generate a response right now: {str(e)}"
        except Exception as e:
            return f"Something went wrong generating the response: {str(e)}"
        