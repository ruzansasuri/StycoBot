# OG chatbot code.
import random

# Global variables
BOT_NAME = "StycoBot"
user_name = None

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
user_name = None

def authenticate_user():
    """
    Authenticate a user by checking if they exist in the known names.
    
    This function prompts the user for their name and verifies if it exists
    in the known_names set. Sets the global user_name variable and exits if the user is not found.
    
    Returns:
        None: If authentication succeeds
    """
    global user_name
    user_name = input("Please enter your name: ")
    if user_name not in known_names:
        print(f"Sorry {user_name}, I'm not there yet. Soon, I will be able to learn about new people. Till then ask about Ruzan.")
        exit(0)
    print(f"Welcome back {user_name}! I'm {BOT_NAME}.")

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


def run_sql_command(_command):
    """Not used in this version"""
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
    
def print_help():
    """
    Display available chatbot commands.
    
    This function prints a list of commands that users can use to interact with
    the chatbot, including how to ask about food preferences, age, and quotes.
    """
    print("Type 'quit' to exit.")
    print("Type 'help' for instructions.")   
    print("Type 'change name' to change your name.")
    print("Available commands:")
    print("- Ask about food preferences")
    print("- Ask about age")
    print("- Ask about favorite quotes")
    print("- Type anything else for a random response")

def print_welcome():
    """Print the welcome message and available commands"""
    print(f"Welcome to {BOT_NAME}!")
    print("Type 'help' for instructions.")

def print_salutation():
    """Print a salutation message"""
    print(f"Hello! I'm {BOT_NAME}. I can chat with you about people I know and their favorite food, age, and quotes.")

def print_salutation_user():
    """Print a salutation message"""
    global user_name
    print(f"Hello {user_name}! I'm {BOT_NAME}.")
    print("Once you are done talking with me you can change your name by typing 'change name'.")

def communicate():
    while True:
        user_input = input("\nYou: ")
        
        # Handle exit commands
        if user_input.lower() == 'quit':
            break
        # Show help menu
        elif user_input.lower() == 'help':
            print_help()
            continue
        elif user_input.lower() == 'change name':
            authenticate_user()
            continue
            
        # Extract name from input
        name = extract_name(user_input)
        print("log: name = ", name  )
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
        print(f"\n{BOT_NAME}: {response}")

def print_goodbye():
    """Print a goodbye message"""
    print(f"Goodbye! Have a great day!")

def main():
    global user_name
    print_welcome()
    authenticate_user()
    print_salutation_user()
    communicate()
    print_goodbye()

if __name__ == '__main__':
    main()