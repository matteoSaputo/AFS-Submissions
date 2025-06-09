from tkinter import messagebox
import zipfile
import os

def extract_zip(zip_path):
    extracted = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip:
            zip.extractall(os.path.dirname(zip_path))
            for name in zip.namelist():
                extracted_path = os.path.join(os.path.dirname(zip_path), name)
                extracted.append(extracted_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract {os.path.basename(zip_path)}")
    return extracted