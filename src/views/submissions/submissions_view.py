import tkinter as tk
from PIL import Image, ImageTk


class SubmissionsView(tk.Frame):
    def __init__(self, controller, root):
        super().__init__(root, bg=controller.bg_color)
        self.root = root
        self.controller = controller
        self.bg_color = controller.bg_color
        self.dnd_bg_color = controller.dnd_bg_color
        self.version = controller.version
        self.drive = controller.drive

        self.spinner_running = False
        self.spinner_frame = 0
        self.spinner_path = self.controller.model.resource_path("assets/spinner.gif")

        # --- UI Elements ---
        self.title_label = tk.Label(
            self, 
            text="Upload AFS Application", 
            font=("Segoe UI", 18, "bold"), 
            bg=self.bg_color
        )
        self.title_label.pack(pady=(30, 20))

        self.change_drive_btn = tk.Button(
            self,
            text="Change Drive Folder",
            font=("Segoe UI", 12),
            command=controller.change_drive_path,
            bg="#007BFF",
            fg="white",
            width=20
        )
        self.change_drive_btn.pack(pady=(0, 10))

        self.drive_label = tk.Label(
            self,
            text="Drive: (not selected)",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg="gray"
        )
        self.drive_label.pack(pady=(0, 20))
        if self.drive:
            self.drive_label.config(text=f"Drive: {self.drive}")
        else:
            self.drive_label.config(text="Drive: (not selected)")

        self.drop_frame = tk.Frame(
            self,
            width=650,
            height=200,
            bg=self.dnd_bg_color,
            highlightbackground="gray",
            highlightthickness=2
        )
        self.drop_frame.pack(pady=10)

        self.configure_dnd(self.drop_frame)

        self.drop_target_register('DND_Files')
        self.dnd_bind('<<Drop>>', controller.handle_drop)

        self.scroll_canvas = tk.Canvas(self.drop_frame, bg=self.dnd_bg_color, highlightthickness=0)
        self.scroll_frame = tk.Frame(self.scroll_canvas, bg=self.dnd_bg_color)
        self.scrollbar = tk.Scrollbar(
            self.drop_frame, 
            orient="vertical",
            command=self.scroll_canvas.yview
        )

        self.scroll_canvas.config(yscrollcommand=self.scrollbar.set)

        self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )

        self.drop_frame.bind(
            "<MouseWheel>",
            lambda event: self.scroll_canvas.yview_scroll(int(-1 * (event.delta/120)), "units") 
        )

        self.configure_dnd(self.scroll_canvas)
        self.configure_dnd(self.scroll_frame)

        self.upload_btn = tk.Button(
            self.drop_frame, 
            text="Click to Select File(s)\nor Drag and Drop", 
            font=("Segoe UI", 14), 
            command=controller.upload_pdf, 
            bg="#007BFF", 
            fg="white", 
            width=20, 
            height=2
        )
        self.upload_btn.place(relx=0.5, rely=0.5, anchor="center")

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
        self.match_label.pack(pady=20)

        self.folder_button_frame = tk.Frame(self, bg=self.bg_color)
        self.folder_button_frame.pack(pady=10)

        self.confirm_btn = tk.Button(
            self.folder_button_frame, 
            text="✅ Use This Folder", 
            font=("Segoe UI", 12), 
            command=controller.confirm_folder, 
            bg="#28a745", 
            fg="white", 
            state=tk.DISABLED,
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
            state=tk.DISABLED,
            width=20
        )
        self.new_folder_btn.pack(side="left", padx=15)

        self.version_label = tk.Label(
            self,
            text=f"Version: {self.version}",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg="gray"
        )
        self.version_label.pack(side="bottom", pady=10)

        self.clear_files_btn = tk.Button(
            self,
            text="Clear",
            font=("Segoe UI", 14),
            command=lambda: [controller.model.clean_uploads_folder(), controller.reset_folder_UI()],
            bg="#545151",
            fg="white",
            width=10,
            height=1
        )
        self.clear_files_btn.pack(side="bottom", pady=10)

    def configure_dnd(self, widget):
        widget.drop_target_register('DND_Files')
        widget.dnd_bind('<<Drop>>', self.controller.handle_drop)

        # Allow clicking to open file dialog
        widget.bind("<Button-1>", lambda event: self.controller.upload_pdf())

        widget.dnd_bind('<<DragEnter>>', lambda e: widget.config(bg="#d0f0d0"))
        widget.dnd_bind('<<DragLeave>>', lambda e: widget.config(bg=self.dnd_bg_color))