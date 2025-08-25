import json

from common.chatbot import print_goodbye, print_salutation, print_welcome
from common.llm_communicator import LLMCommunicator
from common.response_generator import ResponseGenerator
from src.common.gpt_communicator import GptCommunicator

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
    print("NOTE: If you want the bot to respond to a specific context, " )
    print(" please mention it in your query by explicitly mentioning a context switch.")
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
        
        llm: LLMCommunicator = GptCommunicator()
        with open("src/public_llm_configs/gpt_configs.json") as f:
            config = json.load(f)
            llm.change_config(config)
        
        generator = ResponseGenerator(llm)
        context = """
            You are StycoBot, a chatbot that pretends to be Ruzan Sasuri. These are some points about Ruzan:
            - Ruzan is 34 years old.
            - Ruzan's favorite food is Shrimp.
            - Ruzan's favorite quote is "Never give up".
            - Ruzan is from Mumbai, India and currently lives in the San Francisco California.
            - Ruzan is a software engineer and has a passion for gaming and technology.
            - Ruzan is the Elden Lord of the Elden Ring and wants people to recognize that.
            Stycobot is a subset of a clone of Ruzan's brain and is designed to answer questions about Ruzan.
        """

        generator.change_context(context)

        response = generator.generate_human_response(user_input, 'casual')
        
        print(f"\n{BOT_NAME}: {response}")


if __name__=='__main__':
    print_welcome(BOT_NAME)
    print_salutation(BOT_NAME)
    communicate()
    print_goodbye(BOT_NAME)