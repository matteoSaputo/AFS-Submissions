import os
import re
from rapidfuzz import process, fuzz

# Normalize a business name string
def normalize_name(name):
    name = name.lower()
    name = re.sub(r"(llc|inc|corp|co|l\.l\.c\.|dba|ltd|pllc|s-corp|s corp|c corp)", "", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip()

# Find best matching folder
def find_matching_folder(business_name, base_folder):
    normalized_business = normalize_name(business_name)
    existing_folders = [f for f in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, f))]

    normalized_folders = {folder: normalize_name(folder) for folder in existing_folders}

    # Use fuzzy matching to find the closest match
    best_match = process.extractOne(
        normalized_business,
        normalized_folders.values(),
        scorer=fuzz.token_sort_ratio
    )

    if best_match:
        match_score = best_match[1]
        matched_normalized_name = best_match[0]

        # Find the original folder that corresponds to the normalized match
        matched_folder = next((folder for folder, norm in normalized_folders.items() if norm == matched_normalized_name), None)

        if match_score > 90:
            print(f"Auto-selected folder: '{matched_folder}' ({match_score}% match)")
            return os.path.join(base_folder, matched_folder)

        elif 50 <= match_score <= 90:
            print(f"\nPotential match: '{matched_folder}' ({match_score}% match)")
            print(f"🔍 Incoming name: '{business_name}'")
            response = input("Use this folder? [Y/n]: ").strip().lower()
            if response in ("y", "yes", ""):
                return os.path.join(base_folder, matched_folder)
            else:
                print("User chose to create a new folder.")
                return None
            
    print("New folder created")
    return None  # no good match found
