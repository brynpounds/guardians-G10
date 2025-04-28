# session_tracking.py

import time

def create_player_session(r, email):
    session_key = f"session:{email}"
    r.hset(session_key, mapping={
        "email": email,
        "current_score": 0,
        "tickets_completed": 0,
        "mode": "structured",  # or unstructured
        "last_activity": str(int(time.time()))
    })

def get_player_session(r, email):
    session_key = f"session:{email}"
    if r.exists(session_key):
        return r.hgetall(session_key)
    return None
