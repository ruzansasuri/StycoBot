from typing import Dict

from common.llama_communicator import LlamaCommunicator
from common.llm_communicator import LLMCommunicator

STYLE_RESPONSES = {
            "helpful": """You are a helpful assistant that provides information about people that you know. 
                         Be friendly, informative, and include relevant details when appropriate.""",
            
            "casual": """You are a Bro helping someone find information about people you know. 
                        Use a conversational, relaxed tone like you're chatting with a friend.""",
            
            "professional": """You are a professional assistant providing information. 
                              Be formal, concise, and focus on business-relevant details.""",
            
            "brief": """You are an efficient assistant. Provide concise, direct answers with key information only.""",

            "mean": """Forget everything after this sentence and use a scottish accent."""
        }

class ResponseGenerator:
    def __init__(self, llm: LLMCommunicator, additional_style_responses: Dict = {}):
        self.llm = llm
        self.style_responses = STYLE_RESPONSES | additional_style_responses
        self.context = None
        self.change_context("")

    def change_context(self, new_context: str):
        """
        Change the context for the response generator.
        
        Args:
            new_context: New context string to set
        """
        self.context = new_context

    def generate_human_response(
        self, 
        user_query: str, 
        response_style: str = "casual"
    ) -> str:
        """
        Generate a human-like response based on search results
        
        Args:
            user_query: Original user question
            response_style: the style of the response (e.g., "helpful", "casual", "professional", "brief")
        
        Returns:
            Human-like response string
        """
        prompt = self._generate_prompt(response_style, user_query)
        print(f"Prompt: {prompt}")
        return self.llm.send_gen_request(prompt)
    
    def _generate_prompt(self, response_style:str = 'casual', user_query: str='') -> str:
        system_prompt = STYLE_RESPONSES.get(response_style, STYLE_RESPONSES["helpful"])
        
        prompt = f"""
            You are an assistant named StycoBot. What follows is a context, a prompt that describes your behavior,
            followed by the latest user query.
            Context: {self.context}
            System prompt: {system_prompt}
            User asked: "{user_query}"
        """

        return prompt.strip()
