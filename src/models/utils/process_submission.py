"""
process_submission: Utilities for preparing and processing AFS submissions.

Handles extraction, overlaying defaults, redaction, folder matching, contract rendering, and migration to drive.
"""

from models.utils.afs_parser import extract_afs_data
from models.utils.overlay_default_vlaues_afs import overlay_default_values_afs
from models.utils.redact_contact_info import redact_contact_info
from models.utils.find_matching_folder import find_matching_folder
from models.utils.generate_business_name import generate_business_name
from models.utils.render_contract import generate_context, render_contract, convert_docx_to_pdf
from models.utils.resource_path import resource_path
from models.utils.migrate_to_drive import migrate_to_drive
from models.utils.flatten_pdf import flatten_pdf
from models.utils.fill_template import fill_pdf

import os
import re

# --- Aplication Templates --- 
AFS_TEMPLATE = resource_path("data/templates/applications/New Official Business Application (Fillable).pdf")
NRS_TEMPLATE = resource_path("data/templates/applications/NRS Funding Application (Fillable).pdf")
ARF_TEMPLATE = resource_path("data/templates/applications/ARF Stella Application (Fillable).pdf")
FUNDSHOP_TEMPLATE = resource_path("data/templates/applications/Fundshop Funding Application (Fillable).pdf")

# --- Contract Templates ---
LOC_AGREEMENT_TEMPLATE = resource_path("data/templates/agreements/Master Line of Credit Agreement - VCG.docx")
AUTHORIZATION_FEE_SHEET_TEMPLATE = resource_path("data/templates/agreements/Authorization Fee Sheet.pdf")
HELOC_AGREEMENT_TEMPLATE = resource_path("data/templates/agreements/HELOC Agreement Template.pdf")

def prepare_submission(afs_path: str, drive, document_purpose):
    """Prepare submission data and related fields for processing.

    Parameters
    ----------
    afs_path : str
        Path to the AFS application file.
    drive : str
        Path to the drive folder.
    document_purpose : str
        Purpose of the document (e.g., application type).

    Returns
    -------
    tuple
        Extracted data, missing values, file type, business name, matched folder, match score, full package.
    """
    afs_data, missing_values, file_type, full_package = extract_afs_data(afs_path, document_purpose)
    if full_package:
        return afs_data, None, file_type, None, None, None, full_package
    legal_name = afs_data.get("Business Legal Name")
    if not legal_name:
        legal_name = afs_data.get("Merchant Name")
    bus_name, matched_folder, match_score = prepare_fields(
        drive, 
        legal_name=legal_name,
        dba_name=afs_data.get("DBA", "")
    )
    return afs_data, missing_values, file_type, bus_name, matched_folder, match_score, full_package

def prepare_fields(drive, legal_name, dba_name):
    """Prepare business name and match folder for submission.

    Parameters
    ----------
    drive : str
        Path to the drive folder.
    legal_name : str
        Legal name of the business.
    dba_name : str
        DBA name of the business.

    Returns
    -------
    tuple
        Business name, matched folder, match score.
    """
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
    """Process an AFS submission, generate PDFs, and move files to the customer folder.

    Parameters
    ----------
    upload_path : str
        Path to uploaded PDF or CSV.
    attatchements : list
        List of uploaded attachments.
    afs_data : dict
        Extracted data dictionary.
    missing_values : dict
        Dictionary of missing values.
    file_type : str
        File type (e.g., '.pdf', '.csv').
    bus_name : str
        Sanitized business name string.
    customer_folder : str
        Confirmed or created folder.
    Returns
    -------
    list
        List of processed attachment file paths.
    """
    # --- File Paths ---
    business_application = resource_path(f"data/uploads/Business Application - {bus_name}.pdf")
    business_sub_application = resource_path(f"data/uploads/Business Sub Application - {bus_name}.pdf")
    nrs_application = resource_path(f"data/uploads/NRS Funding Application - {bus_name}.pdf")
    arf_application = resource_path(f"data/uploads/ARF Stella Application - {bus_name}.pdf")
    fundshop_application = resource_path(f"data/uploads/Fundshop Funding Application - {bus_name}.pdf")

    attatchements.remove(upload_path)
    if file_type == '.pdf':
        overlay_default_values_afs(upload_path, resource_path('temp_path.pdf'), missing_values)
        os.replace(resource_path('temp_path.pdf'), upload_path)

    if file_type == '.csv':
        print(afs_data)
        attatchements.append(
            fill_pdf(
                afs_data, 
                business_application, 
                AFS_TEMPLATE, 
                sig_coords=(180, 685, 360, 785),
                flatten=True,
                signature=afs_data["Owner Name"] 
            )
        )
    else:
        attatchements.append(flatten_pdf(upload_path, business_application))

    # Create the customer folder if it doesn't exist
    os.makedirs(customer_folder, exist_ok=True)

    # Save a copy of the AFS app WITHOUT contact info
    attatchements.append(redact_contact_info(business_application, business_sub_application))

    # Fill and save NRS Application if not CA or VA
    if not afs_data["Business State"] or afs_data.get("Business State", "").lower() not in ['ca', 'california', 'cali', 'va', 'virginia']:
        attatchements.append(
            fill_pdf(
                afs_data, 
                nrs_application, 
                NRS_TEMPLATE, 
                sig_coords=(120, 705, 300, 805),
                signature=afs_data["Owner Name"] 
            )
        )

    # Fill and save ARF Application
    attatchements.append(
        fill_pdf(
            afs_data,
            arf_application,
            ARF_TEMPLATE,
            sig_coords=(120, 675, 300, 775),
            signature=afs_data["Owner Name"]
        )
    )

    # Fill and save fundshop application
    names = afs_data["Owner Name"].split(" ")
    initials_list = [name[0] for name in names]
    initials = "".join(initials_list)
    attatchements.append(
        fill_pdf(
            afs_data,
            fundshop_application,
            FUNDSHOP_TEMPLATE,
            sig_coords=(100, 810, 280, 910),
            signature=initials
        )
    )

    # Move bank statements and other attatchements
    migrate_to_drive(attatchements, customer_folder)

    return attatchements

def process_contracts(upload_path, attatchements: list, afs_data: dict, bus_name: str, customer_folder: str):
    """Process a contract submission, generate agreements, and move files to the customer folder.

    Parameters
    ----------
    upload_path : str
        Path to uploaded contract file.
    attatchements : list
        List of uploaded attachments.
    afs_data : dict
        Extracted contract data.
    bus_name : str
        Sanitized business name string.
    customer_folder : str
        Confirmed or created folder.
    Returns
    -------
    list
        List of processed contract file paths.
    """
    # loc_agreement = resource_path(f"data/uploads/Line of Credit Agreement - {bus_name}.pdf")
    loc_agreement = resource_path(f"data/uploads/Line of Credit Agreement - {bus_name}.pdf")
    fee_sheet = resource_path(f"data/uploads/Authorization Fee Sheet - {bus_name}.pdf")
    heloc_agreement = resource_path(f"data/uploads/AFS Line of Credit - {bus_name}.pdf")

    attatchements.remove(upload_path)

    # Create the customer folder if it doesn't exist
    os.makedirs(customer_folder, exist_ok=True)

    # Generate LOC agreement
    print(afs_data)
    context = generate_context(afs_data)
    print(context)
    contract_doc = render_contract(
        LOC_AGREEMENT_TEMPLATE,
        resource_path("data/uploads/temp.docx"),
        context
    )
    if afs_data.get("Line of Credit") and afs_data.get("Initial Funding"):
        convert_docx_to_pdf(contract_doc, loc_agreement)
        attatchements.append(loc_agreement)
        
        # Generate Fee Sheet
        if not afs_data["Fee"] == '0.0%':
            attatchements.append(
                fill_pdf(
                    afs_data, 
                    fee_sheet,
                    AUTHORIZATION_FEE_SHEET_TEMPLATE,
                    flatten=True,
                    sign=False
                )
            )

    # Generate HELOC agreement
    if afs_data.get("HELOC Amount"):
        if not afs_data.get("HELOC Rate"): 
            afs_data["HELOC Rate"] = "WSJ Prime + 3-6%"
        attatchements.append(
            fill_pdf(
                afs_data, 
                heloc_agreement,
                HELOC_AGREEMENT_TEMPLATE,
                flatten=True,
                sign=False
            )
        )

    migrate_to_drive(attatchements, customer_folder)

    return attatchements

