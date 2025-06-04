from models.utils.afs_parser import extract_afs_data
from models.utils.fill_nrs import fill_nrs
from models.utils.redact_contact_info import redact_contact_info
from models.utils.find_matching_folder import find_matching_folder
from models.utils.generate_business_name import generate_business_name
from models.utils.resource_path import resource_path
from models.utils.migrate_to_drive import migrate_to_drive
from models.utils.flatten_pdf import flatten_pdf

import os
import re

def prepare_submission(afs_path, drive):
    afs_data = extract_afs_data(afs_path)

    # Create a cleaned business name
    if not afs_data.get("Business Legal Name") and afs_data.get("DBA"):
        bus_name = re.sub(r'[\\/*?:."<>|]', "", afs_data["DBA"])
    else:
        bus_name = re.sub(r'[\\/*?:."<>|]', "", afs_data["Business Legal Name"])

    if afs_data.get("DBA"):
        dba = re.sub(r'[\\/*?:."<>|]', "", afs_data["DBA"])
        bus_name = generate_business_name(bus_name, dba)

    # Suggest a folder match but don't make it yet
    matched_folder, match_score = find_matching_folder(
        bus_name,
        drive,
        legal_name=afs_data.get("Business Legal Name", ""),
        dba_name=afs_data.get("DBA", "")
    )

    return afs_data, bus_name, matched_folder, match_score


def process_submission(upload_path, attatchements, afs_data, bus_name, customer_folder):
    """
    Takes in:
    - upload_path: path to uploaded PDF (e.g., "./data/uploads/document.pdf")
    - attatchements: list of uploaded attatchements
    - afs_data: extracted data dictionary
    - bus_name: sanitized business name string
    - customer_folder: confirmed or created folder
    """
    # --- File Paths ---
    business_application = resource_path(f"data/uploads/Business Application - {bus_name}.pdf")
    business_sub_application = resource_path(f"data/uploads/Business Sub Application - {bus_name}.pdf")
    nrs_application = resource_path(f"data/uploads/NRS Funding Application - {bus_name}.pdf")

    # Rename afs app with business name
    if not os.path.exists(business_application):
        flatten_pdf(upload_path, business_application)
    attatchements.remove(upload_path)
    attatchements.append(business_application)

    # Create the customer folder if it doesn't exist
    os.makedirs(customer_folder, exist_ok=True)

    # Save a copy of the AFS app WITHOUT contact info
    attatchements.append(redact_contact_info(business_application, business_sub_application))

    # Fill and save NRS Application
    attatchements.append(fill_nrs(afs_data, nrs_application))

    # Move bank statements and other attatchements
    migrate_to_drive(attatchements, customer_folder)

    return attatchements
