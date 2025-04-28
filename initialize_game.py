# initialize_game.py

import redis
import time
import json
from response_keyword_abstraction import extract_keywords, normalize_with_custom_synonyms

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

DEBUG_MODE = True

UNSTRUCTURED_ISSUES = {
    "2001": {
        "description": "TALOS is not configured at Site9"
    },
    "2002": {
        "description": "TALOS is not configured at Site10"
    },
    "2003": {
        "description": "Umbrella is not configured at Site10"
    },
    "2004": {
        "description": "You are missing the license for a MS120-8 switch"
    }
}

def load_unstructured_issues():
    issue_list_key = "unstructured_issue_list"

    if DEBUG_MODE:
        print("\n[INIT] Checking for unstructured issues...")

    if r.llen(issue_list_key) == 0:
        if DEBUG_MODE:
            print("[INIT] Loading unstructured issues...")

        for issue_id, issue_data in UNSTRUCTURED_ISSUES.items():
            issue_key = f"unstructured:{issue_id}"
            description = issue_data["description"]

            # 🔥 Canonicalize it!
            extracted = extract_keywords(description, debug=False)
            normalized = normalize_with_custom_synonyms(extracted)

            r.hset(issue_key, mapping={
                "description": description,
                "canonical_normalized": json.dumps(normalized)
            })

            r.rpush(issue_list_key, issue_id)

        if DEBUG_MODE:
            print(f"[INIT] Loaded {len(UNSTRUCTURED_ISSUES)} unstructured issues.")
    else:
        if DEBUG_MODE:
            print(f"[INIT] {r.llen(issue_list_key)} unstructured issues already exist.")


CANONICAL_EXTRACTION_PROMPT = """You are a network troubleshooting assistant.

Given a diagnostic sentence and a list of Canonical Technical Terms, your job is to:

- Extract technical concepts, action verbs, specific details, locations, and problems.
- For technical concepts, always normalize to the Canonical Term closest in meaning to what the sentence says.
- Only pick from the Canonical Technical Terms provided.
- Do not invent new technical concepts.

Categories:
1. Technical Feature (normalized to Canonical Terms) such as Spanning Tree Protocol, or Border Gateway Protocol. Get as close to the technical feature as you can if one is not clear.
2. Verbs / Actions - such as applied, configured, set, enabled, disabled, or similar words.
3. Specific Details - details beyond the main Technical Feature. Example: "Bandwidth Throttle set to 10 Meg" — Bandwidth Throttle would be the Technical Feature. 10 Meg would be the details.
4. Location - If included, extract the location where the issue is happening.
5. Problem Description - Describe the problem in canonical terms.
6. Root Cause - try to determine the root cause in canonical terms.

Respond ONLY in this JSON format:
{
  "technical_concepts": [],
  "verbs_actions": [],
  "specific_details": [],
  "location": [],
  "problem": [],
  "root cause": []
}

Canonical Technical Terms:"""

TROUBLE_TICKETS = {
    "1001": {
        "description": "Users at Site4 are experiencing network-wide loops and disconnections.",
        "root_cause": "Spanning Tree Protocol is disabled"
    },
    "1002": {
        "description": "Users can't connect to WiFi in Chicago — authentication failures observed.",
        "root_cause": "Pre-Shared Key for wireless is incorrect"
    },
    "1003": {
        "description": "Internet is slow in Bowling Green — traffic heavily throttled.",
        "root_cause": "Bandwidth Throttle feature incorrectly configured at 10 Mbps"
    },
    "1004": {
        "description": "There are intermittent network issues in Owensborro.",
        "root_cause": "CPU on the Meraki MX is high due to heavy traffic on VLAN 101"
    }
}


def normalize_root_cause(raw_text):
    extracted = extract_keywords(raw_text, debug=False)
    normalized = normalize_with_custom_synonyms(extracted)

    return normalized  # Keep as structured dictionary!

def store_canonical_prompt():
    r.set("canonical_extraction_prompt", CANONICAL_EXTRACTION_PROMPT)
    print("[INIT] Canonical Extraction Prompt saved to Redis.")

def load_trouble_tickets():
    ticket_list_key = "ticket_list"

    if DEBUG_MODE:
        print("\n[INIT] Checking for trouble tickets...")

    if r.llen(ticket_list_key) == 0:
        if DEBUG_MODE:
            print("[INIT] Loading trouble tickets...")

        for ticket_id, ticket_data in TROUBLE_TICKETS.items():
            ticket_key = f"ticket:{ticket_id}"
            description = ticket_data["description"]
            root_cause_raw = ticket_data["root_cause"]
            root_cause_normalized = normalize_root_cause(root_cause_raw)

            r.hset(ticket_key, mapping={
                "description": description,
                "root_cause": root_cause_raw,
                "root_cause_normalized": json.dumps(root_cause_normalized)  # Save as JSON string!
            })
            r.rpush(ticket_list_key, ticket_id)

        if DEBUG_MODE:
            print(f"[INIT] Loaded {len(TROUBLE_TICKETS)} trouble tickets.")
    else:
        if DEBUG_MODE:
            print(f"[INIT] {r.llen(ticket_list_key)} trouble tickets already exist.")

def run_initialization():
    print("\n🚀 Initializing Game Environment...")
#    store_canonical_prompt()
    load_trouble_tickets()
    load_unstructured_issues()
    print("\n✅ Initialization Complete.")

if __name__ == "__main__":
    run_initialization()

