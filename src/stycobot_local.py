from chatbot import print_goodbye, print_salutation, print_welcome
from llm_to_db import DatabaseSearcher
from response_generator import ResponseGenerator

# Global variables
BOT_NAME = "StycoBot"

def print_help():
    """
    Display available chatbot commands.
    
    This function prints a list of commands that users can use to interact with
    the chatbot, including how to ask about food preferences, age, and quotes.
    """
    print("Type 'quit' to exit.")
    print("Type 'help' for instructions.")   
    print("Available commands:")
    print("- Ask about a particular person by name(Currently only Ruzan).")
    print("- Ask about food preferences")
    print("- Ask about age")
    print("- Ask about favorite quotes")
    print("- Type anything else for a random response")

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

        searcher = DatabaseSearcher("people.db")
        generator = ResponseGenerator()

        results = searcher.search(user_input, method="hybrid")
        print(f"Found: {results}")
        response = generator.generate_human_response(user_input, results, 'casual')
        

        print(f"\n{BOT_NAME}: {response}")


if __name__=='__main__':
    print_welcome()
    print_salutation()
    communicate()
    print_goodbye()