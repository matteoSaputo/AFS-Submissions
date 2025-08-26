import tkinter as tk
from tkinter import ttk

from models.main_model import MainModel
from views.components.drop_frame import DropFrame
from views.components.change_drive_btn import DriveChanger

BTN_COLOR = "#0F20B4"
DND_BG_COLOR = "#f0f0f0"

class ContractsView(tk.Frame):
    def __init__(self, root, controller, model: MainModel, bg):
        super().__init__(root)
        self.root = root
        self.bg_color = bg
        self.configure(bg=bg)
        self.model = model
        self.controller = controller

        # --- UI Elements ---
        self.title_label = tk.Label(
            self, 
            text="Upload Application or LOC Agreement", 
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

        # --- options row ---
        options = tk.Frame(
            self, 
            bg=DND_BG_COLOR,
            padx=10,
            pady=10,
            highlightbackground="gray",
            highlightthickness=2
        )
        options.pack(padx=16, pady=(8, 12))

        tk.Label(options, text="Percent Fee", font=("Segoe UI", 10, "bold"),
                 fg="#000000", bg=bg).grid(row=0, column=0, sticky="w")
        self.fee_combo = ttk.Combobox(
            options, state="readonly",
            values=[f"{p/10}%" for p in range(0, 41)]
        )
        self.fee_combo.set("4.0%")
        self.fee_combo.grid(row=1, column=0, sticky="w", padx=(0, 16))

        tk.Label(options, text="Frequency", font=("Segoe UI", 10, "bold"),
                 fg="#000000", bg=bg).grid(row=0, column=1, sticky="w")
        self.freq_combo = ttk.Combobox(
            options, state="readonly", values=["Weekly", "Daily"],
        )
        self.freq_combo.set("Weekly")
        self.freq_combo.grid(row=1, column=1, sticky="w", padx=(0, 16))

        tk.Label(options, text="Interest", font=("Segoe UI", 10, "bold"),
                 fg="#000000", bg=bg).grid(row=0, column=2, sticky="w")
        self.freq_combo = ttk.Combobox(
            options, state="readonly", values=[1.00, 1.25, 1.50]
        )
        self.freq_combo.set(1.50)
        self.freq_combo.grid(row=1, column=2, sticky="w", padx=(0, 16))
        
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