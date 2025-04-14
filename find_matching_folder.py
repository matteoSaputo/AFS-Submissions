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
    print(f"Best Match: {best_match}")
    if best_match and best_match[1] > 90:  # Confidence threshold
        # Return the original folder name (not the normalized one)
        for folder, norm in normalized_folders.items():
            if norm == best_match[0]:
                print("Found matching folder")
                return os.path.join(base_folder, folder)

    print("New folder created")
    return None  # no good match found
