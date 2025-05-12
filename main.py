import tkinter as tk
from tkinterdnd2 import TkinterDnD
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

import os
import shutil
import threading

# Import relevant modules
from modules.process_submission import process_submission, prepare_submission
from modules.afs_parser import extract_afs_data
from modules.resource_path import resource_path
from modules.user_data import get_user_data_path
from modules.get_version import get_version

# --- Global constants ---
UPLOAD_DIR = resource_path("data/uploads")
VERSION = get_version()

# Create upload dir if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Main application ---
class AFSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AFS Submission Tool")
        self.root.geometry("700x800")
        self.root.configure(bg="#f7f7f7")

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

        # --- UI Elements ---
        self.title_label = tk.Label(
            root, 
            text="Upload AFS Application", 
            font=("Segoe UI", 18, "bold"), 
            bg="#f7f7f7"
        )
        self.title_label.pack(pady=(30, 20))

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

        self.drive_label = tk.Label(
            root,
            text="Drive: (not selected)",
            font=("Segoe UI", 10),
            bg="#f7f7f7",
            fg="gray"
        )
        self.drive_label.pack(pady=(0, 20))
        if self.drive:
            self.drive_label.config(text=f"Drive: {self.drive}")
        else:
            self.drive_label.config(text="Drive: (not selected)")
        
        self.upload_btn = tk.Button(
            root, 
            text="Select File(s)", 
            font=("Segoe UI", 14), 
            command=self.upload_pdf, 
            bg="#4CAF50", 
            fg="white", 
            width=20, 
            height=2
        )
        self.upload_btn.pack(pady=10)
        
        self.drop_frame = tk.Frame(
            root,
            width=400,
            height=150,
            bg="#f0f0f0",
            highlightbackground="gray",
            highlightthickness=2
        )
        self.drop_frame.pack(pady=10)

        self.drop_label = tk.Label(
            self.drop_frame,
            text="Drag and Drop File(s) Here\nor Click to Browse",
            font=("Arial", 12),
            bg="#f0f0f0"
        )
        self.drop_label.place(relx=0.5, rely=0.5, anchor="center")

        self.drop_frame.drop_target_register('DND_Files')
        self.drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # --- Spinner setup ---
        self.spinner_frames = []
        spinner_path = resource_path("assets/spinner.gif")
        img = Image.open(spinner_path)

        # Create a Canvas (instead of Label) for the spinner
        self.spinner_canvas = tk.Canvas(root, width=100, height=100, highlightthickness=0, bg="#f7f7f7")
        self.spinner_canvas_image = None

        # Load all frames
        try:
            while True:
                frame = ImageTk.PhotoImage(img.copy().convert('RGBA'))  # ensure transparency preserved
                self.spinner_frames.append(frame)
                img.seek(len(self.spinner_frames))  # move to next frame
        except EOFError:
            pass

        # Allow clicking to open file dialog
        self.drop_frame.bind("<Button-1>", lambda event: self.upload_pdf())

        self.drop_frame.dnd_bind('<<DragEnter>>', lambda e: self.drop_frame.config(bg="#d0f0d0"))
        self.drop_frame.dnd_bind('<<DragLeave>>', lambda e: self.drop_frame.config(bg="#f0f0f0"))

        self.root.drop_target_register('DND_Files')
        self.root.dnd_bind('<<Drop>>', self.handle_drop)

        self.match_label = tk.Label(
            root, 
            text="", 
            font=("Segoe UI", 12), 
            bg="#f7f7f7"
        )
        self.match_label.pack(pady=20)

        self.confirm_btn = tk.Button(
            root, 
            text="✅ Use This Folder", 
            font=("Segoe UI", 12), 
            command=self.confirm_folder, 
            bg="#28a745", 
            fg="white", 
            state=tk.DISABLED,
            width=20
        )
        self.confirm_btn.pack(pady=5)

        self.new_folder_btn = tk.Button(
            root, 
            text="❌ Create New Folder", 
            font=("Segoe UI", 12), 
            command=self.create_new_folder, 
            bg="#dc3545", 
            fg="white", 
            state=tk.DISABLED,
            width=20
        )
        self.new_folder_btn.pack(pady=5)

        self.version_label = tk.Label(
            root,
            text=f"Version: {VERSION}",
            font=("Segoe UI", 10),
            bg="#f7f7f7",
            fg="gray"
        )
        self.version_label.pack(side="bottom", pady=10)

    def upload_pdf(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if not file_paths:
            return
        self.handle_files(file_paths)

    def handle_drop(self, event):
        self.drop_frame.config(bg="#d0f0d0")
        dropped_files = self.root.tk.splitlist(event.data)
        pdf_files = [os.path.abspath(f.strip('{}')) for f in dropped_files]
        self.handle_files(pdf_files)
        self.drop_frame.config(bg="#f0f0f0")

    def clean_uploads_folder(self):
        files_to_delete =[f for f in os.listdir(UPLOAD_DIR) if f != "keep.txt"]

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

    def handle_files(self, file_list):
        self.show_spinner()

        def process():
            self.clean_uploads_folder()
            self.uploaded_files =[]

            for original_path in file_list:
                filename = os.path.basename(original_path)
                dest_path = os.path.join(UPLOAD_DIR, filename)
                shutil.copy(original_path, dest_path)
                self.uploaded_files.append(dest_path)
            
            self.selected_application_file = self.uploaded_files[0]
            for file in self.uploaded_files:
                if extract_afs_data(file):
                    self.selected_application_file = file
            
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
            self.match_label.config(text="")
            self.confirm_btn.config(state=tk.DISABLED)
            self.new_folder_btn.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to process: {str(e)}")

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

# --- Start app ---
if __name__ == "__main__":
    root = TkinterDnD.Tk()    
    app = AFSApp(root)
    root.mainloop()
    app.clean_uploads_folder()