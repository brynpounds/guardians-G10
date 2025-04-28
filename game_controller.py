# game_controller.py (monster badass final version)

import redis
import random
import json
from response_keyword_abstraction import extract_keywords, normalize_with_custom_synonyms
from structured_grading import generate_summary_text, score_similarity, llm_score_player_response
from player_feedback import generate_feedback

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

        # 📋 Display Side-by-Side Comparison
        fields = ["technical_concepts", "verbs_actions", "specific_details", "location", "problem", "root cause"]

        print("\n📝 Canonical Extraction Comparison:\n")
        print(f"{'Field':<22} | {'Canonical Root Cause':<40} | {'Player Diagnosis':<40}")
        print("-" * 110)

        for field in fields:
            canonical_value = expected_normalized.get(field, [])
            player_value = player_normalized.get(field, [])

            # Convert lists to short readable strings
            canonical_str = ", ".join(canonical_value) if isinstance(canonical_value, list) else str(canonical_value)
            player_str = ", ".join(player_value) if isinstance(player_value, list) else str(player_value)

            print(f"{field:<22} | {canonical_str:<40} | {player_str:<40}")

        print("-" * 110)

        # 🧠 Semantic similarity scoring
        expected_summary = generate_summary_text(expected_normalized)
        player_summary = generate_summary_text(player_normalized)
        semantic_score = score_similarity(expected_summary, player_summary)

        # 🛠 Strict structured field-by-field scoring

        expected_summary = generate_summary_text(expected_normalized)
        player_summary = generate_summary_text(player_normalized)

        semantic_score = score_similarity(expected_summary, player_summary)

        strict_score, reason = llm_score_player_response(expected_normalized, player_normalized, debug=True)

        print(f"\n🏆 Semantic Similarity Score: {semantic_score} / 100")
        print(f"🏆 LLM Structured Score: {strict_score} / 100")
        print(f"\n💬 LLM Feedback:\n{reason}")

        # 🧠 Generate LLM feedback
        feedback = generate_feedback(expected_normalized, player_normalized)

        # 🏆 Show all results
        print(f"\n🏆 Semantic Similarity Score: {semantic_score} / 100")
        print(f"🏆 LLM Structured Score: {strict_score} / 100")

        print(f"\n💬 LLM Feedback:\n{feedback}")

        # Ask to continue
        again = input("\n🔁 Grab another ticket? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    main_loop()

