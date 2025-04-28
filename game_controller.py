# game_controller.py (switching to Unstructured Testing Mode)

import redis
import random
import json
from response_keyword_abstraction import extract_keywords, normalize_with_custom_synonyms
#from structured_grading import generate_summary_text, score_similarity, grade_response
from unstructured_grading import summarize_keywords, evaluate_unstructured

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def fetch_random_unstructured_issue():
    issue_ids = r.lrange("unstructured_issue_list", 0, -1)
    if not issue_ids:
        print("❌ No unstructured issues found in Redis.")
        return None

    random_issue_id = random.choice(issue_ids)
    issue_key = f"unstructured:{random_issue_id}"
    issue_data = r.hgetall(issue_key)
    return issue_data

def main_loop():
    print("\n🚀 Welcome to Unstructured Canonical Extraction Testing Mode")

    while True:
        issue = fetch_random_unstructured_issue()
        if not issue:
            print("❌ No unstructured issue available.")
            break

        print("\n🛠️ Unstructured Network Issue (Player-Facing Description):")
        print(issue['description'])

        # Load expected Canonical normalized root cause
        try:
            expected_normalized = json.loads(issue['canonical_normalized'])
        except Exception as e:
            print(f"⚠️ Error decoding unstructured normalized root cause: {e}")
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

        # 🧠 Summarize for scoring
        expected_summary = summarize_keywords(expected_normalized)
        player_summary = summarize_keywords(player_normalized)

        # 🏆 Score it
        score, feedback = evaluate_unstructured(expected_summary, player_summary)

        # 🎯 Display results
        print(f"\n🏆 Player Score: {score} / 100")
        print("\n💬 LLM Feedback:")
        print(feedback)


        print("-" * 110)

        # ✏️ Commented out for now — save for structured mode later
        #
        # expected_summary = generate_summary_text(expected_normalized)
        # player_summary = generate_summary_text(player_normalized)
        #
        # score = score_similarity(expected_summary, player_summary)
        #
        # structured_score, feedback = grade_response(expected_normalized, player_normalized, debug=True)
        #
        # print(f"\n🏆 Semantic Similarity Score: {score} / 100")
        # print(f"🏆 Structured Field-by-Field Score: {structured_score} / 100")
        # print("\n💬 LLM Feedback:")
        # print(feedback)

        # Ask to continue
        again = input("\n🔁 Grab another unstructured issue? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    main_loop()

