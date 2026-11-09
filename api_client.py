# api_client.py
import os
import requests
from dotenv import load_dotenv

# Load the secret keys from the .env file
load_dotenv()

def execute_prompt(provider, model_name, prompt):
    """
    Routes the prompt to the correct API provider and returns the AI's response.
    Supports Groq, OpenRouter, and Google Gemini.
    """
    provider = provider.lower()
    
    if provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        api_key = os.getenv("GROQ_API_KEY")
    elif provider == "openrouter":
        url = "https://openrouter.ai/api/v1/chat/completions"
        api_key = os.getenv("OPENROUTER_API_KEY")
    elif provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    else:
        raise ValueError(f"Unsupported provider: {provider}")

    # Safety check: If real keys aren't set yet, return a simulated response
    if not api_key or "your_" in api_key:
        return f"[Simulated Response from {model_name}] - Add real {provider} API key to test live."

    # Gemini uses its own specific JSON structure
    if provider == "gemini":
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        except requests.exceptions.RequestException as e:
            return f"API Connection Error: {str(e)}"
            
    # Groq and OpenRouter share the standard OpenAI structure
    else:
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
    print("Testing Multi-Provider API Connector (Simulation Mode)...")
    
    test_groq = execute_prompt("groq", "llama-3.1-8b-instant", "Test")
    test_openrouter = execute_prompt("openrouter", "meta-llama/llama-3.1-8b-instruct", "Test")
    test_gemini = execute_prompt("gemini", "gemini-1.5-flash", "Test")
    
    print(f"Groq Result: {test_groq}")
    print(f"OpenRouter Result: {test_openrouter}")
    print(f"Gemini Result: {test_gemini}")