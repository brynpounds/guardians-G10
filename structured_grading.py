# structured_grading.py

from response_keyword_abstraction import normalize_with_custom_synonyms

def grade_response(normalized_keywords, expected_root_cause, debug=False):
    """
    Grade player response by normalizing both the player response and
    the expected root cause for better matching.
    """
    expected_raw = expected_root_cause.lower().strip()

    # Normalize expected root cause into the same structure
    expected_normalized = normalize_with_custom_synonyms({
        "technical_concepts": [expected_raw],
        "verbs_actions": [],
        "specific_details": [],
        "location": [],
        "problem": []
    })

    # Combine normalized fields
    combined_expected_text = " ".join(expected_normalized.get("technical_concepts", []) +
                                      expected_normalized.get("problem", [])).lower()

    combined_player_text = " ".join(normalized_keywords.get("technical_concepts", []) +
                                    normalized_keywords.get("problem", [])).lower()

    match_found = combined_expected_text in combined_player_text or combined_player_text in combined_expected_text

    score = 100 if match_found else 0

    if debug:
        print("\n[DEBUG] Grading Breakdown:")
        print(f"- Expected Root Cause (Raw): {expected_raw}")
        print(f"- Expected Normalized Words: {expected_normalized}")
        print(f"- Combined Expected Text: '{combined_expected_text}'\n")

        print(f"- Player Normalized Keywords: {normalized_keywords}")
        print(f"- Combined Player Text: '{combined_player_text}'\n")

        print(f"[MATCHING LOGIC]")
        if match_found:
            print(f"✅ MATCH FOUND: Player keywords matched expected normalized root cause.")
        else:
            print(f"❌ NO MATCH: Player keywords did not match expected normalized root cause.")

        print(f"Score Awarded: {score}\n")

    return score
