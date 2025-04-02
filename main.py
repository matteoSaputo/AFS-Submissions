from afs_parser import extract_afs_data
from fill_nrs import fill_nrs
from pdfrw import PdfReader, PdfWriter

import os
import re
import shutil

def rewrite_pdf(input_path, output_path):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    writer.addpages(reader.pages)
    writer.write(output_path)

def main():

    # Extract data from afs application
    afs_data = extract_afs_data("Business Application.pdf")

    # Sanitize business name to avoid accidentally making weird folders
    bus_name = re.sub(r'[\\/*?:"<>|]', "_", afs_data["Business Legal Name"])
    
    customer_folder = f'G:\Shared drives\AFS Drive\Customer Info\Customer Info/{bus_name}'

    # Create the customer folder if it doesn't exist
    os.makedirs(customer_folder, exist_ok=True)

    # Save afs app in new folder
    rewrite_pdf("Business Application.pdf", f"{customer_folder}/Business Application - {bus_name}")

    # Fill and save NRS Application
    fill_nrs(afs_data, customer_folder)

if __name__ == "__main__":
    main()