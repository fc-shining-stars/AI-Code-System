# augment.py
import openai
import os
from dotenv import load_dotenv
from reasoner import Reasoner

# Load environment variables from .env file
load_dotenv()

# Configure the client for DeepSeek's API
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("Please set the DEEPSEEK_API_KEY environment variable in your .env file.")

# Create the client instance
deepseek_client = openai.OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

class Augment:
    def __init__(self):
        self.reasoner = Reasoner(deepseek_client)

    def get_user_input(self, prompt="\n[Augment] Welcome to the DeepSeek AI System. What would you like to build?\n> "):
        """Gets input from the user."""
        return input(prompt)

    def send_to_reasoner(self, user_request):
        """Sends the user request to the Reasoner and handles iterative Q&A."""
        print(f"\n[Augment] Sending request to Reasoner: '{user_request}'")
        
        # This is the iterative loop. It continues until Reasoner is satisfied.
        while True:
            response = self.reasoner.analyze(user_request)
            
            # Check if the response is a question from the Reasoner
            if response.startswith("QUESTION:"):
                # Extract the question and ask the user
                question = response.replace("QUESTION:", "").strip()
                print(f"\n[Augment] The AI needs more information: {question}")
                user_answer = self.get_user_input("Your Answer > ")
                
                # Append the user's answer to the original request for context
                user_request += f" {user_answer}"
            else:
                # If it's not a question, it's the final result
                print("[Augment] Received final response from Reasoner.")
                return response

    def display_response(self, response):
        """Displays the final response from the system."""
        print(f"\n[Augment] Final Output:\n{response}")

if __name__ == "__main__":
    agent = Augment()
    initial_request = agent.get_user_input()
    final_response = agent.send_to_reasoner(initial_request)
    agent.display_response(final_response)