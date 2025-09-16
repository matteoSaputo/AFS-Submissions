import os
import shutil

from models.utils.flatten_pdf import flatten_pdf

def migrate_to_drive(files, drive):
    # Move files from "files" list into folder "drive"
    for file in files:
        if not file or not os.path.exists(file):
            continue
        flatten_pdf(file, file)
        new_path = os.path.join(drive, os.path.basename(file))
        if os.path.exists(new_path):
            os.unlink(new_path)
        shutil.move(file, drive)