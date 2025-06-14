import json
import random

# Global variables
BOT_NAME = "StycoBot"

class UserData:
    def __init__(self, name, age, food, quote):
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

def extract_name(user_input: str) -> str:
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

def get_user_data(name):
    """Get user data from in-memory data"""
    if name in known_names:
        user = USERS[name]
        return [user.name, user.age, user.food, user.quote]
    return None

def generate_response(user_data, user_input):
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

def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: The event data from the API Gateway
        context: The runtime context
        
    Returns:
        dict: Response containing status code and message
    """
    try:
        # Get the user input from the event
        body = json.loads(event.get('body', '{}'))
        user_input = body.get('message', '')
        
        # Extract name from input
        name = extract_name(user_input)
        
        if name is None:
            response = "I didn't find a name in your message.\n" + \
                      "Try asking about someone I know,\n" + \
                      "or ask them to chat with me first so I can learn about them."
        else:
            # Get user data
            user_data = get_user_data(name)
            
            # Remove the name from input if it was found
            if name in user_input:
                user_input = user_input.replace(name, '').strip()
            
            response = generate_response(user_data, user_input)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enable CORS
            },
            'body': json.dumps({
                'message': response
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        } 