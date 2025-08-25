# Global variables

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

def print_welcome(bot_name):
    """Print the welcome message and available commands"""
    print(f"Welcome to {bot_name}!")
    print("Type 'help' for instructions.")

def print_salutation(bot_name):
    """Print a salutation message"""
    print(f"Hello! I'm {bot_name}. I can chat with you about people I know and their favorite food, age, and quotes.")

def print_goodbye(bot_name):
    """Print a goodbye message"""
    print(f"This has been {bot_name}. Goodbye! Have a great day!")