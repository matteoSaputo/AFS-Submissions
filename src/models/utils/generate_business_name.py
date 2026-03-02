"""
generate_business_name: Utility for generating clean business names.

Uses legal name and DBA, appending DBA only if sufficiently different.
"""

from rapidfuzz import fuzz
import re

def generate_business_name(legal_name, dba_name, threshold=85):
    """Generate a clean business name using legal name and DBA.

    Parameters
    ----------
    legal_name : str
        Legal name of the business.
    dba_name : str
        DBA name of the business.
    threshold : int, optional
        Similarity threshold for appending DBA (default: 85).

    Returns
    -------
    str
        Cleaned business name.
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
