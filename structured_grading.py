# structured_grading.py

import requests
import json
from sentence_transformers import SentenceTransformer, util

# Initialize Sentence Transformer once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Ollama local LLM setup
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

# --- Scoring Functions ---

def generate_summary_text(normalized_keywords):
    """
    Generate a lightweight text summary from normalized canonical fields.
    """
    parts = []

    for field in ["technical_concepts", "verbs_actions", "specific_details", "location", "problem", "root cause"]:
        entries = normalized_keywords.get(field, [])
        if entries:
            parts.append(", ".join(entries))

    return " | ".join(parts)

def score_similarity(expected_summary, player_summary):
    """
    Score semantic similarity between expected and player summaries.
    """
    expected_embedding = model.encode(expected_summary, normalize_embeddings=True)
    player_embedding = model.encode(player_summary, normalize_embeddings=True)
    similarity = util.cos_sim(expected_embedding, player_embedding)[0][0].item()

    scaled_score = int(similarity * 100)
    return scaled_score

def llm_score_player_response(expected_normalized, player_normalized, debug=False):
    """
    Use LLM to strictly and fairly score the player's answer.
    """

    system_prompt = """
You are a network engineering instructor.

Your job is to evaluate a student's troubleshooting diagnosis for a networking issue.

Strict rules:
- Award FULL CREDIT (100 points) if the student correctly identifies BOTH:
  1. The main Technical Concept (e.g., Spanning Tree Protocol, BGP, PSK)
  2. The main Issue or Problem (e.g., disabled, incorrect, high CPU)

- Award ZERO CREDIT (0 points) if the student identifies ONLY the Technical Concept but misses the Problem.

- Award PARTIAL CREDIT (between 25 and 70 points depending on how close they are) if the student identifies the correct Technical Concept and Problem but misses Specific Details (like VLAN IDs, speeds, or locations).

Tone:
You are a tough but fair teacher. Be encouraging but strict. Giving students too many points would hurt their learning. Reward success accurately.

Respond ONLY in this JSON format:
{
  "score": (integer between 0 and 100),
  "reason": (short explanation why this score was awarded)
}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system_prompt}\n\nCanonical Root Cause (structured JSON):\n{json.dumps(expected_normalized, indent=2)}\n\nPlayer Diagnosis (structured JSON):\n{json.dumps(player_normalized, indent=2)}",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        if response.status_code != 200:
            print(f"⚠️ LLM scoring request failed: {response.text}")
            return 0, "LLM Error"

        raw_response = response.json().get("response", "").strip()

        if debug:
            print("\n[DEBUG] Raw LLM Scoring Response:")
            print(raw_response)

        parsed = json.loads(raw_response)
        return parsed.get("score", 0), parsed.get("reason", "No reason provided.")

    except Exception as e:
        print(f"⚠️ Exception during LLM scoring: {e}")
        return 0, "LLM Exception"


