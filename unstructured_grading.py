# unstructured_grading.py

import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"  # or whatever you're using

# Tough love unstructured grading prompt
UNSTRUCTURED_GRADING_PROMPT = """
You are acting as a strict network troubleshooting instructor evaluating student responses.

Students must be judged harshly but fairly, with no partial credit.

Rules:
- You are helping students become elite network troubleshooters.
- Giving too much credit is harmful to their real-world growth.
- You must be firm but polite — no harsh language or blame.

Scoring Criteria:
- Award 100 points only if the student correctly covers all major elements.
- Award 0 points if the student misses any major elements.

Major elements that must be present:
1. If the original issue mentions a site (e.g., "Site9" or "Site10"), the student's diagnosis MUST specifically reference the correct site.
2. If the original issue includes a technical category (e.g., "TALOS", "Umbrella", "MS120-8"), the student MUST correctly identify that technical concept.
3. If the original issue implies an action or issue (e.g., "not configured", "missing license"), the student MUST correctly state the action or problem.

Additional Instructions:
- NO partial credit is allowed. All required elements must be present for a full score.
- If any element is missing, award 0 points.
- If full credit is awarded, respond: "Well done identifying all key elements!"
- If any element is missing, respond: "We didn't find that issue. Please try again."

Respond ONLY in this strict JSON format:

{
  "score": (integer, 100 or 0),
  "reason": "Brief feedback message."
}
"""

def summarize_keywords(canonical_dict):
    """
    Quickly flatten keywords into a short single sentence for LLM evaluation.
    """
    parts = []
    for field in ["technical_concepts", "verbs_actions", "specific_details", "location", "problem", "root cause"]:
        values = canonical_dict.get(field, [])
        if isinstance(values, list):
            parts.extend(values)
        elif isinstance(values, str):
            parts.append(values)
    return ", ".join(parts)

def evaluate_unstructured(canonical_summary, player_summary):
    """
    Send the canonical and player summaries to the LLM for scoring.
    """
    comparison_prompt = UNSTRUCTURED_GRADING_PROMPT + f"""

Original Network Issue Summary:
{canonical_summary}

Student Diagnosis Summary:
{player_summary}
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": comparison_prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()["response"]

        # Try parsing response
        scoring_result = json.loads(result)
        return scoring_result.get("score", 0), scoring_result.get("reason", "No feedback.")
    except Exception as e:
        print(f"⚠️ LLM scoring error: {e}")
        return 0, "Scoring failed."


