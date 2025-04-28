# player_feedback.py

def generate_feedback(score, debug=False):
    if score > 0:
        return "✅ Great job! You identified the issue!"
    else:
        return "❌ Try again — you missed the core problem."
