"""
migrate_to_drive: Utility for moving files to the drive folder.

Moves files from a list to the specified drive folder, flattening PDFs as needed.
"""

import os
import shutil

from models.utils.flatten_pdf import flatten_pdf_preserving_fields, flatten_pdf

def migrate_to_drive(files, drive):
    """Move files to the drive folder, flattening PDFs if necessary.

    Parameters
    ----------
    files : list
        List of file paths to move.
    drive : str
        Path to the drive folder.
    """
    # Move files from "files" list into folder "drive"
    for file in files:
        if not file or not os.path.exists(file):
            continue
        if os.path.splitext(file)[1] == '.pdf':
            # if "application" not in file.lower():
            if not any(keyword in file.lower() for keyword in ["application", "agreement", "line of credit"]):
                try:
                    flatten_pdf(file, file)
                except Exception as e:
                    print(f"Failed to flatten during migration: {file}", e)
        new_path = os.path.join(drive, os.path.basename(file))
        if os.path.exists(new_path):
            os.unlink(new_path)
        shutil.move(file, drive)