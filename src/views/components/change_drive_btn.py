import tkinter as tk
from tkinter import filedialog, messagebox

from models.main_model import MainModel

class DriveChanger(tk.Frame):
    def __init__(self, root, model: MainModel, bg, btn_color):
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
        drive_path = filedialog.askdirectory(title="Select New Shared Drive Root Folder")
        if self.model.change_drive_path(drive_path):
            self.drive_label.config(text=f"Drive: {self.model.drive}")
            messagebox.showinfo("Drive Updated", "Shared drive path updated successfully!")