"""
extract_zip: Utility for extracting ZIP archives.

Extracts all files from a ZIP archive to the same directory and returns a list of extracted file paths.
"""

import zipfile
import os

def extract_zip(zip_path):
    """Extract all files from a ZIP archive.

    Parameters
    ----------
    zip_path : str
        Path to the ZIP archive.

    Returns
    -------
    list
        List of extracted file paths.
    """
    extracted = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip:
            zip.extractall(os.path.dirname(zip_path))
            for name in zip.namelist():
                extracted_path = os.path.join(os.path.dirname(zip_path), name)
                extracted.append(extracted_path)
    except Exception as e:
        print("Error", f"Failed to extract {os.path.basename(zip_path)}")
    return extracted