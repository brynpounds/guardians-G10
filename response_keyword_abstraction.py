# Add at the top of response_keyword_abstraction.py
import requests
import json
import re
from sentence_transformers import SentenceTransformer, util

# Redis no longer needed since you rolled back (✅ good)

# Ollama Setup
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "mistral"

# Load SentenceTransformer Model
model = SentenceTransformer('all-MiniLM-L6-v2')

custom_synonyms = {
    "TALOS Threat Defense": ["talos", "cisco talos", "talos threat defense"],
    "Spanning Tree Protocol": ["spanning tree", "stp", "802.1d", "spanning tree protocol"],
    "Rapid Spanning Tree Protocol": ["rstp", "802.1w", "rapid spanning tree"],
    "Multiple Spanning Tree Protocol": ["mstp", "802.1s", "multiple spanning tree"],
    "Border Gateway Protocol": ["bgp", "border gateway protocol"],
    "Open Shortest Path First": ["ospf", "open shortest path first"],
    "Network Address Translation": ["nat", "network address translation"],
    "Domain Name System": ["dns", "domain name system"],
    "Dynamic Host Configuration Protocol": ["dhcp", "dynamic host configuration protocol"],
    "Virtual LAN": ["vlan", "virtual lan", "vlan id"],
    "Quality of Service": ["qos", "quality of service"],
    "Access Control List": ["acl", "access control list"],
    "Cisco Umbrella": ["umbrella", "cisco umbrella", "cloud delivered security"],
    "Cisco SecureX": ["securex", "cisco securex"],
    "Cisco XDR": ["xdr", "cisco xdr", "extended detection and response"],
    "Cisco DNA Center": ["dna center", "dnac", "cisco dna c# Add at the top of response_keyword_abstraction.pyenter"],
    "Cisco Identity Services Engine": ["ise", "cisco ise", "identity services engine"],
    "Cisco Secure Group Tags": ["sgt", "secure group tag", "secure group tags", "cisco sgt"],
    "Cisco Meraki MX": ["meraki mx", "mx appliance", "meraki security appliance"],
    "Cisco Meraki MR": ["meraki mr", "meraki access point", "mr access point"],
    "Cisco Meraki MS": ["meraki ms", "meraki switch", "ms switch"],
    "Cisco Meraki Systems Manager": ["meraki sm", "systems manager", "meraki mdm"],
    "Cisco Meraki MV Cameras": ["meraki mv", "meraki camera", "mv camera", "meraki mv camera"],
    "Cisco Meraki MT Sensors": ["meraki mt", "meraki sensors", "mt sensor", "power monitor", "environment sensor"],
    "Meraki Auto VPN": ["auto vpn", "meraki auto vpn", "meraki vpn"],
    "Meraki Traffic Shaping": ["traffic shaping", "meraki traffic shaping", "traffic control"],
    "Meraki Content Filtering": ["content filtering", "meraki content filtering"],
    "802.11 WiFi": ["802.11", "wifi", "wireless lan", "wi-fi"],
    "Service Set Identifier (SSID)": ["ssid", "wireless network name", "wifi ssid"],
    "Pre-Shared Key (PSK)": ["psk", "pre-shared key", "wifi password"],
    "802.1X Authentication": ["802.1x", "dot1x", "wireless 802.1x", "wired 802.1x"],
    "High Availability": ["ha", "high availability", "failover"],
    "Throughput": ["throughput", "bandwidth"],
    "Megabits Per Second": ["mbps", "megs", "meg", "megabits", "mbits"],
    "Gigabits Per Second": ["gbps", "gigs", "gig", "gigabits", "gbits"],
}

def extract_diagnostic_info(sentence, canonical_concepts):
    """
    Use LLM (Mistral) to extract structured JSON output from sentence.
    """
    system_prompt = """You are a network troubleshooting assistant.

Given a diagnostic sentence and a list of Canonical Technical Terms, your job is to:

- Extract technical concepts, action verbs, specific details, locations, and problems.
- For technical concepts, always normalize to the Canonical Term closest in meaning to what the sentence says.
- Only pick from the Canonical Technical Terms provided.
- Do not invent new technical concepts.

Categories:
1. Technical Feature (normalized to Canonical Terms) such as Spanning Tree Protocol, or Border Gateway Protocol. Get as close to the technical feature as you can if one is not clear.
2. Verbs / Actions - such as applied, configured, set, enabled, disabled, or similar words.
3. Specific Details - details beyond the main Technical Feature. Example: "Access Control List is allowing external DNS" — Access Control List would be the Technical Feature. Allowing external DNS would be the details.
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

Canonical Technical Terms:
""" + "\n".join(f"- {concept}" for concept in canonical_concepts) + """

Diagnostic Sentence:
IMPORTANT: Your entire output must be strictly valid JSON. Do not add any text before or after the JSON block.
"""

    full_prompt = f"{system_prompt}\n\"{sentence}\""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    if response.status_code != 200:
        print(f"❌ Ollama error: {response.text}")
        return None

    return response.json()["response"].strip()

def extract_keywords(sentence, debug=False):
    canonical_concepts = sorted(set(custom_synonyms.keys()))
    extraction_result = extract_diagnostic_info(sentence, canonical_concepts)

    try:
        repaired_response = repair_json(extraction_result)
        parsed = json.loads(repaired_response)
    except Exception as e:
        if debug:
            print(f"⚠️ Couldn't parse LLM response after repair attempt: {e}")
        parsed = {}

    if debug:
        print("\n[DEBUG] Raw LLM Extracted Keywords:")
        print(json.dumps(parsed, indent=2))

    return parsed

def normalize_with_custom_synonyms(keywords):
    """
    Basic pass-through normalization.
    (In older version, this didn't do much — so just return as-is for now.)
    """
    return keywords

def repair_json(loose_json_text):
    """
    Attempt to auto-repair common LLM JSON formatting issues:
    - Add missing quotes around keys
    - Remove trailing commas
    - Clean extra whitespace
    """
    repaired = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)\s*:', r'\1"\2":', loose_json_text)
    repaired = re.sub(r',\s*([}\]])', r'\1', repaired)
    repaired = repaired.strip()
    return repaired
