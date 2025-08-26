import tkinter as tk

from models.main_model import MainModel
from views.components.change_drive_btn import DriveChanger
from views.components.drop_frame import DropFrame
from views.components.spinner import Spinner

BTN_COLOR = "#007BFF"

class SubmissionsView(tk.Frame):
    def __init__(self, controller, model: MainModel, root):
        super().__init__(root, bg=controller.bg_color)
        self.root = root
        self.controller = controller
        self.model = model
        
        self.bg_color = controller.bg_color
        self.dnd_bg_color = controller.dnd_bg_color
        
        self.version = model.version
        self.drive = model.drive

        self.spinner_path = self.controller.model.resource_path("assets/spinner.gif")

        self.max_visible_rows = 5

        # --- UI Elements ---
        self.title_label = tk.Label(
            self, 
            text="Upload AFS Application", 
            font=("Segoe UI", 18, "bold"), 
            bg=self.bg_color
        )
        self.title_label.pack(side="top", pady=(30, 20))

        self.change_drive_btn = DriveChanger(
            self, 
            self.model, 
            self.bg_color, 
            btn_color=BTN_COLOR
        )
        self.change_drive_btn.pack()

        self.drop_frame = DropFrame(
            self,
            model=self.model,
            width=650,
            height=200,
            btn_color=BTN_COLOR,
            upload_handler=self.controller.upload_pdf,
            drop_handler=self.controller.handle_drop,
            ui_reset_handler=self.controller.reset_folder_UI,
            delete_file_handler=self.controller.delete_file,
        )
        self.drop_frame.pack(pady=10)

        self.spinner = Spinner(
            root,
            spinner_path=self.spinner_path,
            width=100,
            height=100,
            bg=self.bg_color
        )

        self.match_label = tk.Label(
            self, 
            text="", 
            font=("Segoe UI", 12), 
            bg=self.bg_color
        )

        self.folder_button_frame = tk.Frame(self, bg=self.bg_color)

        self.confirm_btn = tk.Button(
            self.folder_button_frame, 
            text="✅ Use This Folder", 
            font=("Segoe UI", 12), 
            command=controller.confirm_folder, 
            bg="#28a745", 
            fg="white", 
            width=20
        )
        self.confirm_btn.pack(side="left", padx=5)

        self.new_folder_btn = tk.Button(
            self.folder_button_frame, 
            text="❌ Create New Folder", 
            font=("Segoe UI", 12), 
            command=controller.create_new_folder, 
            bg="#dc3545", 
            fg="white", 
            width=20
        )
        self.new_folder_btn.pack(side="left", padx=15)
