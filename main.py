from afs_parser import extract_afs_data
from fill_nrs import fill_nrs
from redact_contact_info import redact_contact_info
from find_matching_folder import find_matching_folder

import os
import re
import shutil

def main():

    afs_source = "./data/Business Application.pdf"

    # Extract data from afs application
    afs_data = extract_afs_data(afs_source)

    # Sanitize business name to avoid accidentally making weird folders
    bus_name = re.sub(r'[\\/*?:."<>|]', "_", afs_data["Business Legal Name"])
    if afs_data.get('DBA'):
        bus_name = f"{bus_name} DBA {afs_data['DBA']}"

    # Rename afs app with business name
    os.rename(afs_source, f"./data/Business Application - {bus_name}.pdf") 
    afs_source = f"./data/Business Application - {bus_name}.pdf"
 
    # Set root folder
    root = "./test"
    root = "G:\Shared drives\AFS Drive\Customer Info\Customer Info"

    # Set destination folder
    customer_folder = find_matching_folder(bus_name, root)
    if not customer_folder:
        customer_folder = f'{root}/{bus_name}'

    # Create the customer folder if it doesn't exist
    os.makedirs(customer_folder, exist_ok=True)

    # Save a copy of the afs app without contact info
    redact_contact_info(afs_source, f"{customer_folder}/Business Sub Application - {bus_name}.pdf")

    # Fill and save NRS Application
    fill_nrs(afs_data, customer_folder)

    # move afs app in new folder
    if os.path.exists(f"{customer_folder}/Business Application - {bus_name}.pdf"):
        os.remove(f"{customer_folder}/Business Application - {bus_name}.pdf")
    shutil.move(afs_source, customer_folder)

if __name__ == "__main__":
    main()