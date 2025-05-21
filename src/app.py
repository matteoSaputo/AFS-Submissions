import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import os
import shutil
import threading
import zipfile

# Import relevant business logic modules
from models.process_submission import process_submission, prepare_submission
from models.afs_parser import is_likely_application
from models.user_data import get_user_data_path
from models.get_version import get_version
from models.resource_path import resource_path

# --- Global constants ---
UPLOAD_DIR = resource_path("data/uploads")
VERSION = get_version()
BG_COLOR = "#f7f7f7"
DND_BG_COLOR = "#f0f0f0"

# Create upload dir if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Main application ---
class AFSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AFS Submission Tool")
        self.root.geometry("800x800")

        self.upload_dir = UPLOAD_DIR
        self.version = VERSION
        self.bg_color = BG_COLOR
        self.dnd_bg_color = DND_BG_COLOR
        self.root.configure(bg=BG_COLOR)

        self.drive = self.load_drive_path()
        self.uploaded_files = []
        self.selected_application_file = None
        self.afs_data = None
        self.bus_name = None
        self.customer_folder = None
        self.matched_folder = None
        self.match_score = None

        self.spinner_running = False
        self.spinner_frame = 0

        self.max_visible_rows = 5

        # --- UI Elements ---
        self.title_label = tk.Label(
            root, 
            text="Upload AFS Application", 
            font=("Segoe UI", 18, "bold"), 
            bg=BG_COLOR
        )
        self.title_label.pack(pady=(30, 20))
        # self.title_label = create_title_label(self)

        self.change_drive_btn = tk.Button(
            root,
            text="Change Drive Folder",
            font=("Segoe UI", 12),
            command=self.change_drive_path,
            bg="#007BFF",
            fg="white",
            width=20
        )
        self.change_drive_btn.pack(pady=(0, 10))
        # self.change_drive_btn = create_change_drive_btn(self)

        self.drive_label = tk.Label(
            root,
            text="Drive: (not selected)",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg="gray"
        )
        self.drive_label.pack(pady=(0, 20))
        if self.drive:
            self.drive_label.config(text=f"Drive: {self.drive}")
        else:
            self.drive_label.config(text="Drive: (not selected)")
        # self.drive_label = create_drive_label(self)

        self.drop_frame = tk.Frame(
            root,
            width=650,
            height=200,
            bg=DND_BG_COLOR,
            highlightbackground="gray",
            highlightthickness=2
        )
        self.drop_frame.pack(pady=10)

        self.drop_frame.drop_target_register('DND_Files')
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # Allow clicking to open file dialog
        self.drop_frame.bind("<Button-1>", lambda event: self.upload_pdf())

        self.drop_frame.dnd_bind('<<DragEnter>>', lambda e: self.drop_frame.config(bg="#d0f0d0"))
        self.drop_frame.dnd_bind('<<DragLeave>>', lambda e: self.drop_frame.config(bg=DND_BG_COLOR))

        self.root.drop_target_register('DND_Files')
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

        self.scroll_canvas = tk.Canvas(self.drop_frame, bg=DND_BG_COLOR, highlightthickness=0)
        self.scroll_frame = tk.Frame(self.scroll_canvas, bg=DND_BG_COLOR)
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

        self.scroll_canvas.drop_target_register('DND_Files')
        self.scroll_canvas.dnd_bind('<<Drop>>', self.handle_drop)

        # Allow clicking to open file dialog
        self.scroll_canvas.bind("<Button-1>", lambda event: self.upload_pdf())

        self.scroll_canvas.dnd_bind('<<DragEnter>>', lambda e: self.scroll_canvas.config(bg="#d0f0d0"))
        self.scroll_canvas.dnd_bind('<<DragLeave>>', lambda e: self.scroll_canvas.config(bg=DND_BG_COLOR))

        self.scroll_frame.drop_target_register('DND_Files')
        self.scroll_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # Allow clicking to open file dialog
        self.scroll_frame.bind("<Button-1>", lambda event: self.upload_pdf())

        self.scroll_frame.dnd_bind('<<DragEnter>>', lambda e: self.scroll_frame.config(bg="#d0f0d0"))
        self.scroll_frame.dnd_bind('<<DragLeave>>', lambda e: self.scroll_frame.config(bg=DND_BG_COLOR))

        self.upload_btn = tk.Button(
            self.drop_frame, 
            text="Click to Select File(s)\nor Drag and Drop", 
            font=("Segoe UI", 14), 
            command=self.upload_pdf, 
            bg="#007BFF", 
            fg="white", 
            width=20, 
            height=2
        )
        self.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
        # self.drop_frame, self.scroll_canvas, self.scroll_frame, self.scrollbar = create_drop_frame(self)
        # self.upload_btn = create_upload_btn(self)

        # --- Spinner setup ---
        self.spinner_frames = []
        spinner_path = resource_path("assets/spinner.gif")
        img = Image.open(spinner_path)

        # Create a Canvas (instead of Label) for the spinner
        self.spinner_canvas = tk.Canvas(root, width=100, height=100, highlightthickness=0, bg=BG_COLOR)
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
            root, 
            text="", 
            font=("Segoe UI", 12), 
            bg=BG_COLOR
        )
        self.match_label.pack(pady=20)

        self.folder_button_frame = tk.Frame(root, bg=BG_COLOR)
        self.folder_button_frame.pack(pady=10)

        self.confirm_btn = tk.Button(
            self.folder_button_frame, 
            text="✅ Use This Folder", 
            font=("Segoe UI", 12), 
            command=self.confirm_folder, 
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
            command=self.create_new_folder, 
            bg="#dc3545", 
            fg="white", 
            state=tk.DISABLED,
            width=20
        )
        self.new_folder_btn.pack(side="left", padx=15)

        self.version_label = tk.Label(
            root,
            text=f"Version: {VERSION}",
            font=("Segoe UI", 10),
            bg=BG_COLOR,
            fg="gray"
        )
        self.version_label.pack(side="bottom", pady=10)

        self.clear_files_btn = tk.Button(
            root,
            text="Clear",
            font=("Segoe UI", 14),
            command=lambda: [self.clean_uploads_folder(), self.reset_folder_UI()],
            bg="#545151",
            fg="white",
            width=10,
            height=1
        )
        self.clear_files_btn.pack(side="bottom", pady=10)

    def upload_pdf(self):
        file_paths = filedialog.askopenfilenames()
        if not file_paths:
            return
        self.handle_files(file_paths)

    def handle_drop(self, event):
        self.drop_frame.config(bg="#d0f0d0")
        dropped_files = self.root.tk.splitlist(event.data)
        pdf_files = [os.path.abspath(f.strip('{}')) for f in dropped_files]
        self.handle_files(pdf_files)
        self.drop_frame.config(bg=DND_BG_COLOR)

    def clean_uploads_folder(self):
        files_to_delete =[
            f for f in os.listdir(UPLOAD_DIR) if f != "keep.txt"
        ]

        if not files_to_delete:
            return
        
        for file in files_to_delete:
            file_path = os.path.join(UPLOAD_DIR, file)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. {e}")

    def update_file_display(self):
        def limit_file_name(file, limit=50):
            name, extension = os.path.splitext(file)
            if len(file) > limit:
                return f"{name[:limit]}...{extension}"
            return file

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.uploaded_files:
            self.hide_file_list_frame()
            return
        self.show_file_list_frame()

        for file in self.uploaded_files:
            row = tk.Frame(self.scroll_frame, bg=DND_BG_COLOR)
            row.pack(fill="x", padx=4, pady=2)

            label = tk.Button(row, text=limit_file_name(os.path.basename(file)), bg=DND_BG_COLOR, anchor="w")
            label.pack(side="left", fill="x", expand=True)

            btn = tk.Button(row, 
                text="❌", 
                command=lambda f=file: self.delete_uploaded_file(f),
                bg=DND_BG_COLOR,
                fg="black",
                padx=6
            )

            if file == self.selected_application_file:
                label.config(bg='#bfbfbf')

            btn.pack(side="right", padx=5)
        
        def make_scrollable_for_file_list(widget):
            if not widget:
                return
            if not self.scrollbar.winfo_ismapped():
                widget.unbind("<MouseWheel>")
            else:
                widget.bind(
                    "<MouseWheel>",
                    lambda event: self.scroll_canvas.yview_scroll(int(-1 * (event.delta/120)), "units") 
                )
            for w in widget.winfo_children():
                make_scrollable_for_file_list(w)
        make_scrollable_for_file_list(self.drop_frame)        

    def delete_uploaded_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            self.uploaded_files.remove(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file {file_path}: {e}")
        
        if file_path == self.selected_application_file:
            self.selected_application_file = None
            self.clean_uploads_folder()
            self.reset_folder_UI()
        
        self.update_file_display()

    def extract_zip(self, zip_path):
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

    def handle_files(self, file_list):
        self.show_spinner()

        def process():          
            extracted_files = []

            for original_path in file_list:
                if original_path.lower().endswith(".zip"):
                    file_list.extend(self.extract_zip(original_path))
                    continue
                extracted_files.append(original_path)

            likely_application = ""
            for file in extracted_files:
                if is_likely_application(file):
                    likely_application = file
                    
            if likely_application:
                self.clean_uploads_folder()
                self.reset_folder_UI()

            for file in extracted_files:
                filename = os.path.basename(file)
                dest_path = os.path.join(UPLOAD_DIR, filename)
                if not os.path.exists(dest_path):
                    shutil.copy(file, dest_path)
                if filename == os.path.basename(likely_application):
                    self.selected_application_file = dest_path
                self.uploaded_files.append(dest_path)

            self.update_file_display()

            if not likely_application:
                self.hide_spinner()
                return
            
            self.start_submission(self.selected_application_file)

        threading.Thread(target=process).start()

    def start_submission(self, upload_path):
        try:
            self.afs_data, self.bus_name, self.matched_folder, self.match_score = prepare_submission(upload_path, self.drive)

            if self.matched_folder:
                self.match_label.config(
                    text=f"Matched Folder:\n{self.matched_folder}\n\nBusiness Name:\n{self.bus_name}\n\nMatch Score: {self.match_score}%"
                )
            else:
                self.match_label.config(text="No match found.\nWill create new folder.")

            self.confirm_btn.config(state=tk.NORMAL)
            self.new_folder_btn.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            
        finally:
            self.hide_spinner()

    def confirm_folder(self):
        self.finalize_submission(use_existing=True)

    def create_new_folder(self):
        self.finalize_submission(use_existing=False)

    def finalize_submission(self, use_existing):
        try:
            if self.matched_folder and use_existing:
                self.customer_folder = os.path.join(self.drive, self.matched_folder)
            else:
                self.customer_folder = os.path.join(self.drive, self.bus_name)
            
            process_submission(
                self.selected_application_file, 
                self.uploaded_files,
                self.afs_data, 
                self.bus_name,
                self.customer_folder
            )

            messagebox.showinfo("Success", "Submission processed successfully!")

            # Reset UI
            self.reset_folder_UI()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process: {str(e)}")

    def reset_folder_UI(self):
        self.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
        self.uploaded_files = []
        self.match_label.config(text="")
        self.confirm_btn.config(state=tk.DISABLED)
        self.new_folder_btn.config(state=tk.DISABLED)
        self.update_file_display()

    def show_file_list_frame(self):
        self.upload_btn.place_forget()
        row_height = 30
        visible_rows = min(len(self.uploaded_files)+1, self.max_visible_rows)
        actual_height = row_height * visible_rows
        max_height = row_height * self.max_visible_rows
        relheight = actual_height / max_height - 0.02

        self.scroll_canvas.place(relx=0.02, rely=0.02, relwidth=0.9, relheight=relheight)
        self.scroll_frame.config(height=relheight)
        
        if len(self.uploaded_files)-1 > self.max_visible_rows:
            self.scrollbar.place(relx=0.92, rely=0.02, relheight=relheight)
        else:
            self.scrollbar.place_forget()


    def hide_file_list_frame(self):    
        self.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
        self.scroll_canvas.place_forget()
        self.scrollbar.place_forget()

    def animate_spinner(self):
        if not self.spinner_running:
            return

        frame = self.spinner_frames[self.spinner_frame]

        if self.spinner_canvas_image is None:
            self.spinner_canvas_image = self.spinner_canvas.create_image(50, 50, image=frame)
        else:
            self.spinner_canvas.itemconfig(self.spinner_canvas_image, image=frame)

        self.spinner_frame = (self.spinner_frame + 1) % len(self.spinner_frames)
        self.root.after(100, self.animate_spinner)

    def show_spinner(self):
        self.spinner_canvas.place(relx=0.5, rely=0.8, anchor="center")
        if not self.spinner_running:
            self.spinner_running = True
            self.animate_spinner()
        self.root.update()
    
    def hide_spinner(self):
        self.spinner_canvas.place_forget()
        self.spinner_running = False
        self.root.update()

    def load_drive_path(self):
        drive_path_file = get_user_data_path("drive_path.txt")   

        if os.path.exists(drive_path_file):
            with open(drive_path_file, "r") as f:
                drive_path = f.read().strip()
                if os.path.exists(drive_path):
                    return drive_path
                else:
                    messagebox.showwarning("Drive not found", "Previously saved drive path is missing. Please select it again.")

        # Ask user to select drive folder
        self.prompt_for_drive()
        drive_path = filedialog.askdirectory(title="Select Shared Drive Root Folder")
        if not drive_path:
            messagebox.showerror("Error", "Drive selection is required. Exiting.")
            self.root.destroy()
            exit()

        # Save selected path
        with open(drive_path_file, "w") as f:
            f.write(drive_path)

        return drive_path

    def change_drive_path(self):
        drive_path = filedialog.askdirectory(title="Select New Shared Drive Root Folder")
        drive_path_file = get_user_data_path("drive_path.txt")   

        if drive_path:
            with open(drive_path_file, "w") as f:
                f.write(drive_path)
            self.drive = drive_path
            self.drive_label.config(text=f"Drive: {self.drive}")
            messagebox.showinfo("Drive Updated", "Shared drive path updated successfully!")

    def prompt_for_drive(self):
        messagebox.showinfo(
            "Select Drive Folder",
            "No drive selected.\n\nPlease choose your Google Drive shared folder before proceeding."
        )
