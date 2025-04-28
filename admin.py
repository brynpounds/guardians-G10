# admin.py

import time

def create_player_account(r, email, password):
    player_key = f"player:{email}"
    r.hset(player_key, mapping={
        "password": password,
        "created": str(int(time.time()))
    })
    print(f"[ADMIN] Created player account: {email}")

# We will add more CRUD operations later!
