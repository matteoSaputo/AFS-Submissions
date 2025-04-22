import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from find_matching_folder import find_matching_folder


def setup_mock_folders(base_path, folder_names):
    os.makedirs(base_path, exist_ok=True)
    for name in folder_names:
        folder_path = os.path.join(base_path, name)
        os.makedirs(folder_path, exist_ok=True)

def run_matching_tests(base_path, test_cases):
    for legal_name, dba in test_cases:
        full_name = f"{legal_name} DBA {dba}" if dba else legal_name
        print("\n----------------------------------")
        print(f"📄 Incoming: {full_name}")
        match = find_matching_folder(full_name, base_path, legal_name, dba)
        print(f"📂 Matched folder: {match if match else 'No match found (new folder will be created)'}")

if __name__ == "__main__":
    base_folder = "./test"

    mock_folders = [
        "Alpha Roofing",
        "PF Distribution Center Inc",
        "Advenis Custom Flooring",
        "RACK AUTOMOTIVE AND DIESEL REPAIR",
        "JRCLARK SERVICES",
        "A & A GARAGE LLLP DBA Vintage Customs",
        "Concepts in Engineering Inc DBA Thomas F Henz PE",
        "Valley Landscaping Services",
        "Super Pro Solutions LLC",
        "Mendez Painting & Drywall",
        "Clark Transport Inc",
        "JC & Sons Contractors",
        "Tina’s Floral Boutique LLC",
        "TechWizards LLC",
        "NuAge Skincare"
    ]

    test_inputs = [
        ("Alpha Roofing LLC", ""),
        ("PF Distribution Center, Inc.", ""),
        ("Advenis Custom Floors", ""),
        ("Rack Automotive & Diesel Repair", ""),
        ("Jimmy Clark", "JRCLARK SERVICES"),
        ("A & A GARAGE LLLP", "Vintage Customs"),
        ("Concepts in Engineering Inc", "Thomas F Henz PE"),
        ("Valley Landscaping Service", ""),
        ("Super Pro Solutions", ""),
        ("Mendez Painting and Drywall", ""),
        ("Clark Transport Incorporated", ""),
        ("JC and Sons Contractors", ""),
        ("Tinas Floral Boutique", ""),
        ("Tech Wizards", ""),
        ("Nu Age Skin Care", "")
    ]

    setup_mock_folders(base_folder, mock_folders)
    run_matching_tests(base_folder, test_inputs)
