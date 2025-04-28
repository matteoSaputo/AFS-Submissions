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

    # Set root folder
    root = "./test"
    root = "G:\Shared drives\AFS Drive\Customer Info\Customer Info"

    # Suggest a folder match but don't make it yet
    match = find_matching_folder(
        bus_name,
        root,
        legal_name=afs_data.get("Business Legal Name", ""),
        dba_name=afs_data.get("DBA", "")
    )

    return afs_data, bus_name, match


def process_submission(afs_source, afs_data, bus_name, customer_folder):

    # Extract data from afs application
    afs_data = extract_afs_data(afs_source)

    # Sanitize business name to avoid accidentally making weird folders
    if not afs_data.get('Business Legal Name') and afs_data.get('DBA'):
        bus_name = re.sub(r'[\\/*?:."<>|]', "", afs_data["DBA"])
    else:
        bus_name = re.sub(r'[\\/*?:."<>|]', "", afs_data["Business Legal Name"])
    if afs_data.get('DBA'):
        dba = re.sub(r'[\\/*?:."<>|]', "", afs_data["DBA"])
        bus_name = generate_business_name(bus_name, dba)

    # Rename afs app with business name
    os.rename(afs_source, f"./data/Business Application - {bus_name}.pdf") 
    afs_source = f"./data/Business Application - {bus_name}.pdf"
 
    # Set root folder
    root = "./test"
    root = "G:\Shared drives\AFS Drive\Customer Info\Customer Info"

    # Set destination folder
    customer_folder = find_matching_folder(
        bus_name,
        root,
        legal_name=afs_data.get("Business Legal Name", ""),
        dba_name=afs_data.get("DBA", "")
    )
    if not customer_folder:
        customer_folder = f'{root}/{bus_name}'

    # Create the customer folder if it doesn't exist
    os.makedirs(customer_folder, exist_ok=True)

    # Save a copy of the afs app without contact info
    redact_contact_info(afs_source, f"{customer_folder}/Business Sub Application - {bus_name}.pdf")

    # Fill and save NRS Application (if not cali)
    state = afs_data["Business State"]
    if state.lower() not in ['ca', 'california', 'cali', 'va', 'virginia']:
        fill_nrs(afs_data, customer_folder, bus_name)

    # move afs app in new folder
    if os.path.exists(f"{customer_folder}/Business Application - {bus_name}.pdf"):
        os.remove(f"{customer_folder}/Business Application - {bus_name}.pdf")
    shutil.move(afs_source, customer_folder)

    return customer_folder

if __name__ == "__main__":
    process_submission()