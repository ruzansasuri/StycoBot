import json
import logging
import re
import numpy as np
from typing import Any, List, Dict
import os
from openai import OpenAI

from libs.metrics.shared_metrics import metrics as aws_metrics_logger
from libs.api.common import create_error_response, create_success_response, get_cors_headers, handle_options_request
from libs.metrics.aws_metrics import LogLevel

# Configure metrics
aws_metrics_logger.init("lambda_stycobot")

BOT_NAME = "StycoBot"
MAX_INPUT_LENGTH = 1000  # Maximum allowed input length

class LambdaRAGBot:
    def __init__(self, file_path: str = None) -> None:
        # Load embeddings from JSON (included in Lambda package)
        self.embeddings_data = self.load_embeddings(file_path)
        self.embeddings_matrix = np.array([item['embedding'] for item in self.embeddings_data])
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
    def load_embeddings(self, file_path: str = None) -> List[Dict]:
        """
            Load embeddings from packaged JSON file
            param file_path: Optional path to the embeddings file(please include trailing slash)
        """
        if file_path is None: # When running on lambda, it won't have a path
            embeddings_path = os.path.join(os.path.dirname(__file__), 'embeddings.json')
        else: # When running locally, it will have a path from the if, name, main part.
            embeddings_path = os.path.join(os.getcwd(), f'{file_path}embeddings.json')
        with open(embeddings_path, 'r') as f:
            return json.load(f)
    
    def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> np.ndarray:
        """Get embedding from OpenAI"""
        response = self.client.embeddings.create(
            input=text,
            model=model
        )
        return np.array(response.data[0].embedding)
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def retrieve_context(self, query: str, n_results: int = 3) -> List[Dict]:
        """Retrieve relevant chunks using cosine similarity"""
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Calculate similarities
        similarities = []
        for i, embedding in enumerate(self.embeddings_matrix):
            similarity = self.cosine_similarity(query_embedding, embedding)
            similarities.append((similarity, i))
        
        # Sort by similarity (descending)
        similarities.sort(reverse=True)
        aws_metrics_logger.log_event('Top similarities', {
            'name': 'similarities', 
            'data': similarities[:n_results]
            }, LogLevel.INFO)
        
        # Return top results
        results = []
        for similarity, idx in similarities[:n_results]:
            results.append({
                'text': self.embeddings_data[idx]['text'],
                'metadata': self.embeddings_data[idx]['metadata'],
                'similarity': similarity
            })
        
        aws_metrics_logger.log_event('Retrieved Context chunk', { 
            'name': 'size', 
            'data': len(results)
            }, LogLevel.INFO)
        
        return results
    
    def generate_response(self, query: str, context_chunks: List[Dict], model: str = "gpt-3.5-turbo") -> str:
        """Generate response using OpenAI"""
        # Combine context
        context = "\n\n".join([chunk['text'] for chunk in context_chunks])
        
        prompt = (
            "Based on the following context, answer the user's question."
            "You are StycoBot, an AI spokesperson for Ruzan Sasuri's career."
            "Ruzan Sasuri is looking for a job based on his skills and experience."
            "You are just helping him spread the word about his skills and experience." 
            "Be as gender agnostic as you can." 
            "Mention Ruzan's contact information if you are going to ask someone to contact them.:\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Answer:"
        )
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def chat(self, query: str) -> Dict:
        """Main RAG workflow"""
        # Retrieve relevant chunks
        context_chunks = self.retrieve_context(query)
        
        # Generate response
        response = self.generate_response(query, context_chunks)
        
        return {
            'answer': response,
            'sources': [
                {
                    'text': chunk['text'][:200] + '...',
                    'metadata': chunk['metadata'],
                    'similarity': chunk['similarity']
                }
                for chunk in context_chunks
            ]
        }
    
def validate_input(user_input: str) -> bool:
    """
    Validate user input for security.
    
    Args:
        user_input: The user's input message
        
    Returns:
        bool: True if input is valid, False otherwise
    """
    if not user_input or not isinstance(user_input, str):
        return False
    
    if len(user_input) > MAX_INPUT_LENGTH:
        return False
    
    # Check for potentially malicious patterns
    malicious_patterns = [
        r'<script.*?>',  # Script tags
        r'javascript:',  # JavaScript protocol
        r'data:',        # Data protocol
        r'vbscript:',    # VBScript protocol
        r'on\w+\s*=',    # Event handlers
    ]
    
    for pattern in malicious_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False
    
    return True

def cors_and_validation(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle CORS and input validation
        param event: The event data from the API Gateway.
        return: origin and body if valid, else error response
        """
        # Get origin for CORS
        origin = event.get('headers', {}).get('origin', '')
        aws_metrics_logger.log_event('Request origin', {
            'name': 'URL',
            'data': origin
            }, LogLevel.INFO)

        # Check if origin is allowed using get_cors_headers
        cors_headers, allowed_origins = get_cors_headers(origin)
        if not cors_headers:
            aws_metrics_logger.log_error(PermissionError(f'Origin not allowed: {origin}'), {
                'name': 'allowed origins',
                'data': allowed_origins
            })
            return create_error_response(403, 'Origin not allowed', origin)
        
        # Get the user input from the event
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            aws_metrics_logger.log_error(json.JSONDecodeError, {
                'name': 'Invalid JSON in request body',
                'data': event.get('body', '')})
            return create_error_response(400, 'Invalid request format', origin)
        return origin, body
        
# Lambda handler
def lambda_handler(event, context) -> Dict[str, Any]:
    """AWS Lambda entry point"""
    
        # Get the user input from the event
    try:
        with aws_metrics_logger.time_operation("Full Event Processing"):
            aws_metrics_logger.log_event('Full event', {'0', json.dumps(event)}, LogLevel.INFO) 
            # Handle OPTIONS request
            if event.get('httpMethod') == 'OPTIONS':
                return handle_options_request(event)
            
            with aws_metrics_logger.time_operation("CORS and Validation"):
                origin, body = cors_and_validation(event)

            user_input = body.get('message', '')
            aws_metrics_logger.log_event('User input', {
                'name': 'query',
                'data': user_input
                }, LogLevel.INFO, include_in_async=False)
            
            # Validate input
            if not validate_input(user_input):
                aws_metrics_logger.log_error(ValueError, {
                    'name': 'input',
                    'data': user_input})
                return create_error_response(400, 'Invalid input', origin)
            
            # Initialize bot (will be cached between invocations)
            if not hasattr(lambda_handler, 'bot'):
                lambda_handler.bot = LambdaRAGBot()
                
            # Process query
            with aws_metrics_logger.time_operation("Chat Processing"):
                result = lambda_handler.bot.chat(user_input)

        aws_metrics_logger.log_event('Chat result', {
            'name': 'response',
            'data': result
            }, LogLevel.INFO, include_in_async=False)
        return create_success_response(result, origin)

        
    except Exception as e:
        aws_metrics_logger.log_error(e)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# For local testing
if __name__ == "__main__":
    # Make sure to set OPENAI_API_KEY environment variable
    if not os.environ.get('OPENAI_API_KEY'):
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
        
    bot = LambdaRAGBot('RAG/embeddings/')
    
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in ['quit', 'exit']:
            break
        
        try:
            result = bot.chat(user_query)
            print(f"\nBot: {result['answer']}")
            print(f"\nSources used: {len(result['sources'])}")
        except Exception as e:
            print(f"Error: {e}")