import os
from dotenv import load_dotenv

# It's good practice to load environment variables at the start
load_dotenv()

def query_analyst(query: str, context: dict):
    """
    Sends a query and financial context to the AI Co-Pilot.
    """
    print("AI Analyst Queried.")

    # Check if the API key is available in the environment
    if not os.getenv("OPENAI_API_KEY"):
        return "AI Analyst is offline. Please configure your API key in a .env file."

    # In the future, this will contain the actual API call logic.
    return f"The AI Analyst is processing your query: '{query}'"
