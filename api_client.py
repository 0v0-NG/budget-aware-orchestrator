# api_client.py
import os
import requests
from dotenv import load_dotenv

# Load the secret keys from the .env file
load_dotenv()

def execute_prompt(provider, model_name, prompt):
    """
    Routes the prompt to the correct API provider and returns the AI's response.
    """
    if provider.lower() == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = os.getenv("GROQ_API_KEY")
    elif provider.lower() == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        api_key = os.getenv("OPENROUTER_API_KEY")
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    # Safety check: If real keys aren't set yet, return a simulated response
    if not api_key or "your_" in api_key:
        return f"[Simulated Response from {model_name}] - Add real {provider} API key to test live."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"API Connection Error: {str(e)}"

# --- Quick Test ---
if __name__ == "__main__":
    print("Testing API Connector (Simulation Mode)...")
    
    test_result = execute_prompt(
        provider="groq", 
        model_name="llama-3.1-8b-instant", 
        prompt="What is the capital of Nigeria?"
    )
    
    print(f"Result: {test_result}")