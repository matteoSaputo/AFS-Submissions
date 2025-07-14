from models.utils.afs_parser import extract_afs_data
from models.utils.overlay_default_vlaues_afs import overlay_default_values_afs
from models.utils.redact_contact_info import redact_contact_info
from models.utils.find_matching_folder import find_matching_folder
from models.utils.generate_business_name import generate_business_name
from models.utils.resource_path import resource_path
from models.utils.migrate_to_drive import migrate_to_drive
from models.utils.flatten_pdf import flatten_pdf
from models.utils.fill_template import fill_pdf

import os
import re

AFS_TEMPLATE = resource_path("data/templates/AFS Application (Fillable).pdf")
NRS_TEMPLATE = resource_path("data/templates/NRS Funding Application.pdf")
ARF_TEMPLATE = resource_path("data/templates/ARF Stella Application.pdf")

def prepare_submission(afs_path: str, drive):
    afs_data, missing_values, file_type, full_package = extract_afs_data(afs_path)
    if full_package:
        return afs_data, None, file_type, None, None, None, full_package
    bus_name, matched_folder, match_score = prepare_fields(
        drive, 
        legal_name=afs_data.get("Business Legal Name", ""),
        dba_name=afs_data.get("DBA", "")
    )
    return afs_data, missing_values, file_type, bus_name, matched_folder, match_score, full_package

def prepare_fields(drive, legal_name, dba_name):
    # Create a cleaned business name
    if not legal_name and dba_name:
        bus_name = re.sub(r'[\\/*?:."<>|]', "", dba_name)
    else:
        bus_name = re.sub(r'[\\/*?:."<>|]', "", legal_name)

    if dba_name:
        dba = re.sub(r'[\\/*?:."<>|]', "", dba_name)
        bus_name = generate_business_name(bus_name, dba)

    # Suggest a folder match but don't make it yet
    matched_folder, match_score = find_matching_folder(
        bus_name,
        drive,
        legal_name,
        dba_name
    )

    return bus_name, matched_folder, match_score

def process_submission(upload_path, attatchements: list, afs_data, missing_values, file_type, bus_name, customer_folder):
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
    arf_application = resource_path(f"data/uploads/ARF Stella Application - {bus_name}.pdf")

    attatchements.remove(upload_path)

    if file_type == '.pdf' and overlay_default_values_afs(upload_path, resource_path('temp_path.pdf'), missing_values):
        os.replace(resource_path('temp_path.pdf'), upload_path)

    if file_type == '.csv':
        attatchements.append(
            fill_pdf(
                afs_data, 
                business_application, 
                AFS_TEMPLATE, 
                (180, 575, 360, 675),
                flatten=True
            )
        )
    else:
        attatchements.append(flatten_pdf(upload_path, business_application))

    # Create the customer folder if it doesn't exist
    os.makedirs(customer_folder, exist_ok=True)

    # Save a copy of the AFS app WITHOUT contact info
    attatchements.append(redact_contact_info(business_application, business_sub_application))

    # Fill and save NRS Application if not CA or VA
    if not afs_data["State"] or afs_data.get("State", "").lower() not in ['ca', 'california', 'cali', 'va', 'virginia']:
        attatchements.append(
            fill_pdf(
                afs_data, 
                nrs_application, 
                NRS_TEMPLATE, 
                (120, 705, 300, 805), 
                flatten=False
            )
        )

    # Fill and save ARF Application
    attatchements.append(
        fill_pdf(
            afs_data,
            arf_application,
            ARF_TEMPLATE,
            (120, 675, 300, 775),
            flatten=False
        )
    )

    # Move bank statements and other attatchements
    migrate_to_drive(attatchements, customer_folder)

    return attatchements
