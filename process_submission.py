from afs_parser import extract_afs_data
from fill_nrs import fill_nrs
from redact_contact_info import redact_contact_info
from find_matching_folder import find_matching_folder
from generate_business_name import generate_business_name

import os
import re
import shutil

def prepare_submission(afs_path):
    afs_data = extract_afs_data(afs_path)

    # Create a cleaned business name
    if not afs_data.get("Business Legal Name") and afs_data.get("DBA"):
        bus_name = re.sub(r'[\\/*?:."<>|]', "_", afs_data["DBA"])
    else:
        bus_name = re.sub(r'[\\/*?:."<>|]', "_", afs_data["Business Legal Name"])

    if afs_data.get("DBA"):
        dba = re.sub(r'[\\/*?:."<>|]', "_", afs_data["DBA"])
        bus_name = generate_business_name(bus_name, dba)

    # Set drive folder
    drive = "./test"
    drive = "D:\Shared drives\AFS Drive\Customer Info\Customer Info"

    # Suggest a folder match but don't make it yet
    matched_folder, match_score = find_matching_folder(
        bus_name,
        drive,
        legal_name=afs_data.get("Business Legal Name", ""),
        dba_name=afs_data.get("DBA", "")
    )

    return afs_data, bus_name, matched_folder, match_score, drive


def process_submission(upload_path, afs_data, bus_name, customer_folder):
    """
    Takes in:
    - upload_path: path to uploaded PDF (e.g., "./data/uploads/document.pdf")
    - afs_data: extracted data dictionary
    - bus_name: sanitized business name string
    - customer_folder: confirmed or created folder
    """

    # Rename afs app with business name
    new_afs_path = f"./data/uploads/Business Application - {bus_name}.pdf"
    os.rename(upload_path, new_afs_path)

    afs_source = new_afs_path

    # Create the customer folder if it doesn't exist
    os.makedirs(customer_folder, exist_ok=True)

    # Save a copy of the AFS app WITHOUT contact info
    redact_contact_info(
        afs_source,
        f"{customer_folder}/Business Sub Application - {bus_name}.pdf"
    )

    # Fill and save NRS Application (if not California/Virginia)
    state = afs_data.get("Business State", "")
    if state.lower() not in ['ca', 'california', 'cali', 'va', 'virginia']:
        fill_nrs(afs_data, customer_folder, bus_name)

    # Move AFS original app into customer folder
    destination_path = f"{customer_folder}/Business Application - {bus_name}.pdf"
    if os.path.exists(destination_path):
        os.remove(destination_path)
    shutil.move(afs_source, customer_folder)

    return customer_folder
