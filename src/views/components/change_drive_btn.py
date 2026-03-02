"""
DriveChanger: UI component for changing the drive folder.

Provides a button and label for selecting and displaying the current drive folder.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from models.main_model import MainModel

class DriveChanger(tk.Frame):
    """Frame for changing the drive folder.

    Parameters
    ----------
    root : tk.Widget
        Parent widget for the frame.
    model : MainModel
        Application model for drive management.
    bg : str
        Background color for the frame.
    btn_color : str
        Button color for the change drive button.
    """

    def __init__(self, root, model: MainModel, bg, btn_color):
        """Initialize the DriveChanger frame and its UI components.

        Parameters
        ----------
        root : tk.Widget
            Parent widget for the frame.
        model : MainModel
            Application model for drive management.
        bg : str
            Background color for the frame.
        btn_color : str
            Button color for the change drive button.
        """
        super().__init__(root, bg=bg)
        self.root = root
        self.model = model
        self.bg_color = bg
        self.btn_color = btn_color

        self.change_drive_btn = tk.Button(
            self,
            text="Change Drive Folder",
            font=("Segoe UI", 12),
            command=self.change_drive_path,
            bg=self.btn_color,
            fg="white",
            width=20
        )
        self.change_drive_btn.pack(side="top", pady=(0, 10))

        self.drive_label = tk.Label(
            self,
            text="Drive: (not selected)",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg="gray"
        )
        self.drive_label.pack(side="top", pady=(0, 20))
        if self.model.drive:
            self.drive_label.config(text=f"Drive: {self.model.drive}")
        else:
            self.drive_label.config(text="Drive: (not selected)")

    def change_drive_path(self):
        """Open a dialog to select a new drive folder and update the label."""
        drive_path = filedialog.askdirectory(title="Select New Shared Drive Root Folder")
        if self.model.change_drive_path(drive_path):
            self.drive_label.config(text=f"Drive: {self.model.drive}")
            messagebox.showinfo("Drive Updated", "Shared drive path updated successfully!")