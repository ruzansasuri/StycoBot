import json
import random
import logging
import os
from typing import Dict, Any, Optional
import re

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Global variables
BOT_NAME = "StycoBot"
MAX_INPUT_LENGTH = 1000  # Maximum allowed input length
# ALLOWED_ORIGINS = ['https://ruzansasuri.com']

class UserData:
    def __init__(self, name: str, age: str, food: str, quote: str):
        self.name = name
        self.age = age
        self.food = food
        self.quote = quote

# Create user data objects
USERS = {
    'Ruzan': UserData('Ruzan', '34', 'Shrimp', 'Never give up'),
}

# Set of known names for quick lookup
known_names = set(USERS.keys())

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

def extract_name(user_input: str) -> Optional[str]:
    """
    Extract the name from the user input if it exists.
    
    Args:
        user_input: The user's input message
        
    Returns:
        str: The extracted name or None if no name is found
    """
    if not user_input:
        return None
    
    current_word = ""
    for char in user_input:
        if char.isalnum():
            current_word += char
        elif current_word and current_word in known_names:
            return current_word
        elif char.isspace():
            current_word = ""
    
    if current_word and current_word in known_names:
        return current_word
    return None

def get_user_data(name: str) -> Optional[list]:
    """Get user data from in-memory data"""
    if name in known_names:
        user = USERS[name]
        return [user.name, user.age, user.food, user.quote]
    return None

def generate_response(user_data: list, user_input: str) -> str:
    """Generate a response based on user data and input"""
    if not user_data:
        return "I don't know that user."    
    name = user_data[0]
    age = user_data[1]
    food = user_data[2]
    quote = user_data[3]
    
    if "food" in user_input.lower():
        return f"{name}, your favorite food is {food}. How about trying something new today?"
    elif "age" in user_input.lower():
        return f"{name}, you're {age} years young!"
    elif "quote" in user_input.lower():
        return f"{name}, your favorite quote is: '{quote}'"
    
    return f"Sorry {name}, I can only talk about food, age, and quotes."

def get_cors_headers(origin: str) -> Dict[str, str]:
    """
    Get CORS headers based on the request origin.
    
    Args:
        origin: The request origin
        
    Returns:
        dict: CORS headers
    """
    # Read ALLOWED_ORIGINS from the environment variable
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'https://ruzansasuri.com').split(',')
    logger.info(f"allowed_origins: {allowed_origins}")
    if origin in allowed_origins or '*' in allowed_origins:
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'POST,OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Max-Age': '86400'
        }
    return {}

def handle_options_request(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle OPTIONS request for CORS preflight.
    
    Args:
        event: The event data from the API Gateway
        
    Returns:
        dict: Response for OPTIONS request
    """
    origin = event.get('headers', {}).get('Origin', '')
    return {
        'statusCode': 200,
        'headers': get_cors_headers(origin),
        'body': ''
    }

def create_error_response(status_code: int, error_message: str, origin: str) -> Dict[str, Any]:
    """
    Create an error response with the given status code and message.
    
    Args:
        status_code: HTTP status code
        error_message: Error message to return
        origin: Request origin for CORS headers
        
    Returns:
        dict: Error response
    """
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(origin),
        'body': json.dumps({
            'error': error_message
        })
    }

def create_success_response(message: str, origin: str) -> Dict[str, Any]:
    """
    Create a success response with the given message.
    
    Args:
        message: Success message to return
        origin: Request origin for CORS headers
        
    Returns:
        dict: Success response
    """
    return {
        'statusCode': 200,
        'headers': get_cors_headers(origin),
        'body': json.dumps({
            'message': message
        })
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function
    
    Args:
        event: The event data from the API Gateway
        context: The runtime context
        
    Returns:
        dict: Response containing status code and message
    """
    try:
        # Log the entire event for debugging
        logger.info(f"Full event: {json.dumps(event)}")
        
        # Handle OPTIONS request
        if event.get('httpMethod') == 'OPTIONS':
            return handle_options_request(event)
        
        # Get origin for CORS
        origin = event.get('headers', {}).get('Origin', '')
        logger.info(f"Extracted origin: {origin}")

        # Check if origin is allowed using get_cors_headers
        cors_headers = get_cors_headers(origin)
        if not cors_headers:
            logger.warning(f"Origin not allowed: {origin}")
            return create_error_response(403, 'Origin not allowed', origin)
        
        # Get the user input from the event
        try:
            body = json.loads(event.get('body', '{}'))
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return create_error_response(400, 'Invalid request format', origin)
        
        user_input = body.get('message', '')
        
        # Validate input
        if not validate_input(user_input):
            logger.warning(f"Invalid input received: {user_input[:100]}...")
            return create_error_response(400, 'Invalid input', origin)
        
        # Extract name from input
        name = extract_name(user_input)
        
        if name is None:
            response = "I didn't find a name in your message.\n" + \
                      "Try asking about Ruzan's age, food, or quote."
        else:
            # Get user data
            user_data = get_user_data(name)
            
            # Remove the name from input if it was found
            if name in user_input:
                user_input = user_input.replace(name, '').strip()
            
            response = generate_response(user_data, user_input)
        
        return create_success_response(response, origin)
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return create_error_response(500, 'Internal server error', origin) 