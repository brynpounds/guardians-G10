# response_normalization.py

def normalize_keywords(extracted_keywords, debug=False):
    # For now, just lowercase everything
    normalized = {}
    for key, values in extracted_keywords.items():
        normalized[key] = [v.lower() for v in values]
    
    if debug:
        print("\n[DEBUG] Normalized Keywords:", normalized)
    return normalized
