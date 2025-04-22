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

def find_matching_folder(full_name, base_folder, legal_name, dba_name):
    # Generate name candidates for comparison
    candidates = {
        "Full": normalize_name(full_name),
        "Legal": normalize_name(legal_name),
        "DBA": normalize_name(dba_name)
    }

    # Get existing folders
    existing_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]
    normalized_folders = {folder: normalize_name(folder) for folder in existing_folders}

    # Prepare a list of (candidate type, match info)
    results = []
    for label, query in candidates.items():
        if query:
            match = process.extractOne(
                query,
                normalized_folders.values(),
                scorer=fuzz.token_sort_ratio
            )
            if match:
                match_name, score, *_ = match  # safely unpack only what we need
                results.append((label, match_name, score))

    # Find best result among all
    if not results:
        print("No matches found.")
        return None

    best = max(results, key=lambda x: x[2])  # x[2] = score
    label, matched_norm, score = best
    matched_folder = next((folder for folder, norm in normalized_folders.items() if norm == matched_norm), None)

    if score > 95:
        print(f"Auto-selected ({label}) folder: '{matched_folder}' ({score}% match)")
        return os.path.join(base_folder, matched_folder)

    elif 50 <= score <= 95:
        print(f"\nPotential match ({label}): '{matched_folder}' ({score}% match)")
        print(f"🔍 Incoming: '{full_name}'")
        response = input("Use this folder? [Y/n]: ").strip().lower()
        if response in ("y", "yes", ""):
            return os.path.join(base_folder, matched_folder)

    print("No good match. A new folder will be created.")
    return None
