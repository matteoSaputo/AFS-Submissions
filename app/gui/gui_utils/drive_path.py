from tkinter import filedialog, messagebox
from modules.user_data import get_user_data_path

import os

def load_drive_path(app):
    drive_path_file = get_user_data_path("drive_path.txt")   

    if os.path.exists(drive_path_file):
        with open(drive_path_file, "r") as f:
            drive_path = f.read().strip()
            if os.path.exists(drive_path):
                return drive_path
            else:
                messagebox.showwarning("Drive not found", "Previously saved drive path is missing. Please select it again.")

    # Ask user to select drive folder
    prompt_for_drive()
    drive_path = filedialog.askdirectory(title="Select Shared Drive Root Folder")
    if not drive_path:
        messagebox.showerror("Error", "Drive selection is required. Exiting.")
        app.root.destroy()
        exit()

    # Save selected path
    with open(drive_path_file, "w") as f:
        f.write(drive_path)

    return drive_path

def change_drive_path(app):
    drive_path = filedialog.askdirectory(title="Select New Shared Drive Root Folder")
    drive_path_file = get_user_data_path("drive_path.txt")   

    if drive_path:
        with open(drive_path_file, "w") as f:
            f.write(drive_path)
        app.drive = drive_path
        app.drive_label.config(text=f"Drive: {app.drive}")
        messagebox.showinfo("Drive Updated", "Shared drive path updated successfully!")

def prompt_for_drive():
    messagebox.showinfo(
        "Select Drive Folder",
        "No drive selected.\n\nPlease choose your Google Drive shared folder before proceeding."
    )