# cleanup.py

import redis

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def full_cleanup():
    keys_to_delete = []

    # Collect all trouble ticket keys
    keys_to_delete.extend(r.keys("ticket:*"))

    # Add core game keys
    keys_to_delete.append("ticket_list")
    keys_to_delete.append("canonical_extraction_prompt")
    keys_to_delete.append("player_list")           # if we add players later
    keys_to_delete.append("session_list")           # if we add sessions
    keys_to_delete.append("scoreboard")             # if we add scores
    keys_to_delete.append("game_settings")          # if we add settings

    for key in keys_to_delete:
        if r.exists(key):
            print(f"[CLEANUP] Deleting key: {key}")
            r.delete(key)

    print("✅ Game Redis keys cleaned.")

if __name__ == "__main__":
    confirmation = input("Are you sure you want to clean game data? (yes/no): ").strip().lower()
    if confirmation == "yes":
        full_cleanup()
    else:
        print("❌ Cleanup aborted.")

