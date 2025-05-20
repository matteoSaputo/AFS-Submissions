from gui.gui_utils.drive_path import change_drive_path

import tkinter as tk

def create_change_drive_btn(app):
    change_drive_btn = tk.Button(
        app.root,
        text="Change Drive Folder",
        font=("Segoe UI", 12),
        command=lambda: change_drive_path(app),
        bg="#007BFF",
        fg="white",
        width=20
    )
    change_drive_btn.pack(pady=(0, 10))
    return change_drive_btn

def create_drive_label(app):
    drive_label = tk.Label(
        app.root,
        text="Drive: (not selected)",
        font=("Segoe UI", 10),
        bg=app.bg_color,
        fg="gray"
    )
    drive_label.pack(pady=(0, 20))
    if app.drive:
        drive_label.config(text=f"Drive: {app.drive}")
    else:
        drive_label.config(text="Drive: (not selected)")
    return drive_label