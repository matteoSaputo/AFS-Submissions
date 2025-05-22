import os
import re
from rapidfuzz import process, fuzz

def normalize_name(name):
    if not name:
        return ""
    name = name.lower()
    name = re.sub(r"(llc|inc|corp|co|l\.l\.c\.|dba|ltd|pllc|s-corp|s corp|c corp)", "", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

def find_matching_folder(business_name, base_folder, legal_name, dba_name):
    candidates = []

    # Prepare candidates: full name, legal name, dba name
    if legal_name:
        candidates.append(legal_name)
    if dba_name:
        candidates.append(dba_name)
    candidates.append(business_name)

    best_match = None
    highest_score = 0

    existing_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
    normalized_folders = {folder: normalize_name(folder) for folder in existing_folders}

    for candidate in candidates:
        result = process.extractOne(
            normalize_name(candidate),
            normalized_folders.values(),
            scorer=fuzz.token_sort_ratio
        )
        if result and result[1] > highest_score:
            highest_score = result[1]
            best_match = result[0]

    if best_match:
        matched_folder = next((folder for folder, norm in normalized_folders.items() if norm == best_match), None)
        return matched_folder, highest_score
    else:
        return None, 0

