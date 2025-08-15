import tkinter as tk
from PIL import Image, ImageTk

from models.main_model import MainModel
from views.components.drop_frame import DropFrame

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

        self.spinner_running = False
        self.spinner_frame = 0
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

        self.change_drive_btn = tk.Button(
            self,
            text="Change Drive Folder",
            font=("Segoe UI", 12),
            command=controller.change_drive_path,
            bg="#007BFF",
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
        if self.drive:
            self.drive_label.config(text=f"Drive: {self.drive}")
        else:
            self.drive_label.config(text="Drive: (not selected)")

        self.drop_frame = DropFrame(
            self,
            self.model,
            self.controller.upload_pdf,
            self.controller.handle_drop,
            self.controller.reset_folder_UI,
            self.controller.delete_file,
        )
        self.drop_frame.pack(pady=10)

        # --- Spinner setup ---
        self.spinner_frames = []
        img = Image.open(self.spinner_path)

        # Create a Canvas for the spinner
        self.spinner_canvas = tk.Canvas(self, width=100, height=100, highlightthickness=0, bg=self.bg_color)
        self.spinner_canvas_image = None 

        # Load all frames
        try:
            while True:
                frame = ImageTk.PhotoImage(img.copy().convert('RGBA'))  # ensure transparency preserved
                self.spinner_frames.append(frame)
                img.seek(len(self.spinner_frames))  # move to next frame
        except EOFError:
            pass

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
