# player_feedback.py

import requests
import json
import redis

# Ollama API (local)
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def generate_feedback(expected_normalized, player_normalized):
    """
    Use LLM to generate personalized feedback based on expected vs player normalized data.
    """
    prompt_intro = """You are a network troubleshooting game assistant.

Compare the expected diagnosis with the player's diagnosis.
Be encouraging, but clearly point out:

- What the player got right
- What important technical concepts or problems the player missed

Format your feedback in 2 short bullet points.

Respond only in plain text.
"""

    expected_summary = json.dumps(expected_normalized, indent=2)
    player_summary = json.dumps(player_normalized, indent=2)

    prompt = f"""{prompt_intro}

Expected Diagnosis (Canonical Normalized Fields):
{expected_summary}

Player Diagnosis (Canonical Normalized Fields):
{player_summary}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code != 200:
        print(f"❌ Ollama error: {response.text}")
        return "⚠️ Feedback unavailable."

    return response.json()["response"].strip()

