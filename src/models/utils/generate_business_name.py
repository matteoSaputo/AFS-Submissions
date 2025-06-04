from rapidfuzz import fuzz
import re

def generate_business_name(legal_name, dba_name, threshold=85):
    """
    Generates a clean business name using legal name and DBA, 
    only appending DBA if it's sufficiently different from legal name.
    """
    # Sanitize both names
    legal_clean = re.sub(r'[\\/*?:."<>|]', "", legal_name.strip())
    dba_clean = re.sub(r'[\\/*?:."<>|]', "", dba_name.strip()) if dba_name else ""

    # Compare similarity
    if dba_clean:
        similarity = fuzz.token_set_ratio(legal_clean.lower(), dba_clean.lower())
        if similarity < threshold:
            return f"{legal_clean} DBA {dba_clean}"

    return legal_clean
