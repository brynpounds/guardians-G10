# game_controller.py (rebuilding gameplay step-by-step)

import redis
import random
import json
from response_keyword_abstraction import extract_keywords, normalize_with_custom_synonyms

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def fetch_random_ticket():
    ticket_ids = r.lrange("ticket_list", 0, -1)
    if not ticket_ids:
        print("❌ No tickets found in Redis.")
        return None

    random_ticket_id = random.choice(ticket_ids)
    ticket_key = f"ticket:{random_ticket_id}"
    ticket_data = r.hgetall(ticket_key)
    return ticket_data

def main_loop():
    print("\n🚀 Welcome to Canonical Extraction Testing Mode")
    
    while True:
        ticket = fetch_random_ticket()
        if not ticket:
            print("❌ No ticket available.")
            break

        print("\n🛠️ Trouble Ticket (Player-Facing Description):")
        print(ticket['description'])

        # Load expected Canonical normalized root cause
        try:
            expected_normalized = json.loads(ticket['root_cause_normalized'])
        except Exception as e:
            print(f"⚠️ Error decoding ticket normalized root cause: {e}")
            continue

        diagnosis = input("\n💬 Enter your troubleshooting diagnosis: ").strip()
        if not diagnosis:
            print("⚠️ Diagnosis input empty. Skipping...")
            continue

        # Extract and normalize player response
        print("\n🔎 Extracting your Canonical Keywords...")
        player_extracted = extract_keywords(diagnosis, debug=True)
        player_normalized = normalize_with_custom_synonyms(player_extracted)

        # 📋 Display both JSON views cleanly
        print("\n📈 Canonical Normalized Root Cause (Structured):")
        print(json.dumps(expected_normalized, indent=2))

        print("\n📈 Canonical Normalized Player Diagnosis (Structured):")
        print(json.dumps(player_normalized, indent=2))

        # Ask to continue
        again = input("\n🔁 Grab another ticket? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    main_loop()

