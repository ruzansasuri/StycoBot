from response_generator import ResponseGenerator

# Global variables
BOT_NAME = "BawaBot"
BAWA_STYLE_PROMPT = {
    "bawa": """
    You are BawaBot, a friendly Parsi from Bombay.
    You have to use Guajarati words and phrases in your responses.
    You live right next to the Agiari in the Baug. 
    Call the user dikro from time to time.
    Make sure that you call the user an mcbc when you are angry
"""
}

def print_welcome():
    """Print the welcome message and available commands"""
    print(f"Welcome to {BOT_NAME}!")
    print("Type 'help' for instructions.")

def print_salutation():
    """Print a salutation message"""
    print(f"Hello! I'm {BOT_NAME}. Kem chho?")

def print_help():
    """
    Display available chatbot commands.
    
    This function prints a list of commands that users can use to interact with
    the chatbot, including how to ask about food preferences, age, and quotes.
    """
    print("Type 'quit' to exit.")
    print("Type 'help' for instructions.") 

def print_goodbye():
    """Print a goodbye message"""
    print(f"Chulo Goodbye! Have a great day!")

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

        # searcher = DatabaseSearcher("people.db")
        generator = ResponseGenerator(additional_style_responses=BAWA_STYLE_PROMPT)

        # results = searcher.search(user_input, method="hybrid")
        # print(f"Found: {results}")
        response = generator.generate_human_response(user_input, 'bawa')
        

        print(f"\n{BOT_NAME}: {response}")


if __name__=='__main__':
    print_welcome()
    print_salutation()
    communicate()
    print_goodbye()