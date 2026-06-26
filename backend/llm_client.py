# llm_client.py

import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Load multiple API keys (comma-separated)
raw_keys = os.getenv("OPEN_ROUTER_API_KEYS", "")
API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]

if not API_KEYS:
    raise RuntimeError("No OpenRouter API keys found in .env")

# Simple round-robin index
_key_index = 0


def _get_next_key():
    global _key_index
    key = API_KEYS[_key_index]
    _key_index = (_key_index + 1) % len(API_KEYS)
    return key


def call_llm(messages, model, max_retries=2, max_tokens=1000):
    last_error = None

    for attempt in range(max_retries):
        for _ in range(len(API_KEYS)):
            api_key = _get_next_key()

            try:
                response = requests.post(
                    OPENROUTER_URL,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost",
                        "X-Title": "HBD-Local-Business-AI"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens
                    },
                    timeout=30
                )

                # ----- Rate limit -----
                if response.status_code == 429:
                    print("⚠️ Rate limit hit, switching API key...")
                    time.sleep(0.5)
                    continue

                # ----- Invalid / exhausted key -----
                if response.status_code in (401, 403):
                    print("❌ Invalid or exhausted API key, switching...")
                    continue

                # ----- Other errors -----
                if response.status_code != 200:
                    print("OpenRouter error:", response.status_code, response.text)
                    last_error = response.text
                    continue

                res_json = response.json()
                msg = res_json["choices"][0]["message"]
                print(f"DEBUG: LLM Raw Content: {msg.get('content', '')[:100]}...")
                return msg

            except requests.exceptions.RequestException as e:
                last_error = e
                continue

    raise RuntimeError(f"LLM call failed after retries: {last_error}")


def get_smart_suggestions(text, lang="en", context="QUERY"):
    """ predicts next 5 words/phrases using OpenRouter with specific context-awareness """
    
    # Map context to human-readable field hints
    field_hint = ""
    if context == "ADD_WIZARD_category": field_hint = "The user is entering a Business Category."
    elif context == "ADD_WIZARD_city": field_hint = "The user is typing an Indian City name."
    elif context == "ADD_WIZARD_state": field_hint = "The user is typing an Indian State name."
    elif context == "QUERY": field_hint = "The user is having a general conversation with an AI assistant."
    
    # If text is empty or marker, ask for starters
    is_empty = text == "[EMPTY]" or not text.strip()
    user_input = "START OF SENTENCE" if is_empty else f'typing "{text}"'

    prompt = (
        f"You are a professional predictive keyboard (like Gboard or SwiftKey).\n"
        f"Language: {lang}\n"
        f"Context: {field_hint}\n"
        f"Current Typed Input: {user_input}\n\n"
        "Predict the next 5 most likely words or very short phrases (MAX 3 WORDS) that the user would type next.\n"
        "Rules:\n"
        "1. Return ONLY a JSON list of strings.\n"
        "2. Keep suggestions very brief and professional.\n"
        "3. Match the start of the current word if the user is in the middle of typing."
    )
    
    # Use a small, very fast model for low-latency suggestions
    model = "google/gemini-2.5-flash-lite" 
    
    try:
        msg = call_llm([{"role": "user", "content": prompt}], model, max_tokens=150)
        content = msg.get("content", "[]")
        
        # SELF-HEALING JSON PARSER
        content = content.strip()
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"): content = content[4:]
        content = content.strip()
        
        import json
        try:
            suggestions = json.loads(content)
        except:
            # Plan B: Regex extraction if JSON fails
            import re
            suggestions = re.findall(r'"([^"]*)"', content)
            
        return [s.strip() for s in suggestions if s.strip()][:5]
    except Exception as e:
        print(f"Suggestion Error: {e}")
        return []