import requests
from typing import List, Dict


class ResponseGenerator:
    def __init__(self, llm_url: str = "http://localhost:11434", model: str = "llama2"):
        self.llm_url = llm_url
        self.model = model
    
    def generate_human_response(
        self, 
        user_query: str, 
        search_results: List[Dict], 
        response_style: str = "casual"
    ) -> str:
        """
        Generate a human-like response based on search results
        
        Args:
            user_query: Original user question
            search_results: List of search results from database
            response_style: "helpful", "casual", "professional", "brief"
        
        Returns:
            Human-like response string
        """
        
        if not search_results:
            return self._generate_no_results_response(user_query, response_style)
        
        # Prepare context from search results
        context = self._prepare_context(search_results, user_query)
        
        # Generate response using llm
        return self._call_llm_for_response(user_query, context, response_style)
    
    def _generate_no_results_response(self, user_query: str, response_style: str) -> str:
        """Generate response when no search results found"""
        
        style_responses = {
            "helpful": f"I couldn't find anyone matching your search for '{user_query}'. Could you try being more specific with names, age, food or a quote? I'm here to help you find the right person!",
            
            "casual": f"Hmm, I don't know '{user_query}'. Maybe try a different name? Or let me know something they like to eat or some quote that they like.",
            
            "professional": f"No records found matching the criteria '{user_query}'. Please provide additional search parameters or contact your mom for assistance.",
            
            "brief": f"No results found for '{user_query}'. Try different search terms."
        }
        
        return style_responses.get(response_style, style_responses["helpful"])

    def _prepare_context(self, search_results: List[Dict], user_query: str) -> str:
        """Prepare context string from search results"""
        context_parts = []
        
        for i, result in enumerate(search_results[:3]):  # Top 3 results
            record = result['record']
            score = result['relevance_score']
            match_type = result['match_type']
            
            # Format person info
            person_info = f"Person {i+1}:"
            person_info += f"\n- Name: {record['name']}"
            person_info += f"\n- Age: {record['age']}"
            person_info += f"\n- Food: {record['food']}"
            person_info += f"\n- Quote: {record['quote']}"
            person_info += f"\n- Relevance Score: {score:.2f}"
            person_info += f"\n- Match Type: {match_type}"
            
            # Add why this person matched
            if 'matched_entities' in result:
                matched = result['matched_entities']
                person_info += f"\n- Matched on: {', '.join(matched.keys())}"
            
            context_parts.append(person_info)
        
        return "\n\n".join(context_parts)
    
    def _call_llm_for_response(
        self, 
        user_query: str, 
        context: str, 
        response_style: str
    ) -> str:
        """Call llm to generate human response"""
        
        # Different prompts for different styles
        style_prompts = {
            "helpful": """You are a helpful assistant that provides information about people that you know. 
                         Be friendly, informative, and include relevant details when appropriate.""",
            
            "casual": """You are a Bro helping someone find information about people you know. 
                        Use a conversational, relaxed tone like you're chatting with a bro.""",
            
            "professional": """You are a professional assistant providing information. 
                              Be formal, concise, and focus on business-relevant details.""",
            
            "brief": """You are an efficient assistant. Provide concise, direct answers with key information only."""
        }
        
        system_prompt = style_prompts.get(response_style, style_prompts["helpful"])
        
        prompt = f"""{system_prompt}

User asked: "{user_query}"

Here are the relevant people I know:

{context}

Please provide a natural, conversational response that:
1. Directly addresses what the user asked
2. Highlights the most relevant person(s)
4. Mentions key details that would be useful
5. Is friendly and helpful in tone
6. Makes the user feel like they are conversing with a human from before emojis existed.

Keep it conversational and avoid just listing data - make it feel like an assistant responding."""
    
        try:
            url = f"{self.llm_url}/api/generate"
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
    
def generate_casual_response(user_query: str, search_results: List[Dict]) -> str:
    """Generate a casual, friendly response"""
    generator = ResponseGenerator()
    return generator.generate_human_response(user_query, search_results, "casual")

def generate_brief_response(user_query: str, search_results: List[Dict]) -> str:
    """Generate a brief, concise response"""
    generator = ResponseGenerator()
    return generator.generate_human_response(user_query, search_results, "brief")
