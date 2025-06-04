import tkinter as tk
from tkinter import filedialog, messagebox

import os
import shutil
import threading

# Import model and view
from models.submissions.submissions_model import SubmissionsModel
from views.submissions.submissions_view import SubmissionsView

# --- Global constants ---
UPLOAD_DIR = "data/uploads"

# --- Main application controller ---
class SubmissionsController:
    def __init__(self, root, BG_COLOR, DND_BG_COLOR):
        self.root = root

        self.model = SubmissionsModel(UPLOAD_DIR)

        self.upload_dir = self.model.upload_dir  
        # Create upload dir if it doesn't exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        self.version = self.model.get_version()
        self.bg_color = BG_COLOR
        self.dnd_bg_color = DND_BG_COLOR

        self.drive = self.load_drive_path()
        self.uploaded_files = []
        self.selected_application_file = None
        self.afs_data = None
        self.bus_name = None
        self.customer_folder = None
        self.matched_folder = None
        self.match_score = None

        self.max_visible_rows = 5

        self.view = SubmissionsView(self, root)

    def upload_pdf(self):
        file_paths = list(filedialog.askopenfilenames())
        if not file_paths:
            return
        self.handle_files(file_paths)

    def handle_drop(self, event):
        self.view.drop_frame.config(bg="#d0f0d0")
        dropped_files = self.root.tk.splitlist(event.data)
        pdf_files = [os.path.abspath(f.strip('{}')) for f in dropped_files]
        self.handle_files(pdf_files)
        self.view.drop_frame.config(bg=self.dnd_bg_color)

    def update_file_display(self):
        def limit_file_name(file, limit=50):
            name, extension = os.path.splitext(file)
            if len(file) > limit:
                return f"{name[:limit]}...{extension}"
            return file

        for widget in self.view.scroll_frame.winfo_children():
            widget.destroy()

        if not self.uploaded_files:
            self.hide_file_list_frame()
            return
        self.show_file_list_frame()

        for file in self.uploaded_files:
            row = tk.Frame(self.view.scroll_frame, bg=self.dnd_bg_color)
            row.pack(fill="x", padx=4, pady=2)

            label = tk.Button(row, text=limit_file_name(os.path.basename(file)), bg=self.dnd_bg_color, anchor="w")
            label.pack(side="left", fill="x", expand=True)

            btn = tk.Button(row, 
                text="❌", 
                command=lambda f=file: self.delete_file(f),
                bg=self.dnd_bg_color,
                fg="black",
                padx=6
            )

            if file == self.selected_application_file:
                label.config(bg='#bfbfbf')

            btn.pack(side="right", padx=5)
        
        def make_scrollable_for_file_list(widget):
            if not widget:
                return
            if not self.view.scrollbar.winfo_ismapped():
                widget.unbind("<MouseWheel>")
            else:
                widget.bind(
                    "<MouseWheel>",
                    lambda event: self.view.scroll_canvas.yview_scroll(int(-1 * (event.delta/120)), "units") 
                )
            for w in widget.winfo_children():
                make_scrollable_for_file_list(w)
        make_scrollable_for_file_list(self.view.drop_frame)        

    def delete_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            self.uploaded_files.remove(file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file {file_path}: {e}")
        
        if file_path == self.selected_application_file:
            self.selected_application_file = None
            self.model.clean_uploads_folder()
            self.reset_folder_UI()
        
        self.update_file_display()

    def handle_files(self, file_list):
        self.show_spinner()

        def process():          
            extracted_files = []

            for original_path in file_list:
                if original_path.lower().endswith(".zip"):
                    file_list.extend(self.model.extract_zip(original_path))
                    continue
                extracted_files.append(original_path)

            likely_application = ""
            for file in extracted_files:
                if self.model.is_likely_application(file):
                    likely_application = file
                    
            if likely_application:
                self.model.clean_uploads_folder()
                self.reset_folder_UI()

            for file in extracted_files:
                filename = os.path.basename(file)
                dest_path = os.path.join(self.upload_dir, filename)
                if not os.path.exists(dest_path):
                    shutil.move(file, dest_path)
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
            self.afs_data, self.bus_name, self.matched_folder, self.match_score = self.model.prepare_submission(upload_path, self.drive)

            if self.matched_folder:
                self.view.match_label.config(
                    text=f"Matched Folder:\n{self.matched_folder}\n\nBusiness Name:\n{self.bus_name}\n\nMatch Score: {self.match_score}%"
                )
            else:
                self.view.match_label.config(text="No match found.\nWill create new folder.")

            self.view.confirm_btn.config(state=tk.NORMAL)
            self.view.new_folder_btn.config(state=tk.NORMAL)

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
            
            self.model.process_submission(
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
        self.view.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
        self.uploaded_files = []
        self.view.match_label.config(text="")
        self.view.confirm_btn.config(state=tk.DISABLED)
        self.view.new_folder_btn.config(state=tk.DISABLED)
        self.update_file_display()

    def show_file_list_frame(self):
        self.view.upload_btn.place_forget()
        row_height = 30
        visible_rows = min(len(self.uploaded_files)+1, self.max_visible_rows)
        actual_height = row_height * visible_rows
        max_height = row_height * self.max_visible_rows
        relheight = actual_height / max_height - 0.02

        self.view.scroll_canvas.place(relx=0.02, rely=0.02, relwidth=0.9, relheight=relheight)
        self.view.scroll_frame.config(height=relheight)
        
        if len(self.uploaded_files)-1 > self.max_visible_rows:
            self.view.scrollbar.place(relx=0.92, rely=0.02, relheight=relheight)
        else:
            self.view.scrollbar.place_forget()

    def hide_file_list_frame(self):    
        self.view.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
        self.view.scroll_canvas.place_forget()
        self.view.scrollbar.place_forget()

    def animate_spinner(self):
        if not self.view.spinner_running:
            return

        frame = self.view.spinner_frames[self.view.spinner_frame]

        if self.view.spinner_canvas_image is None:
            self.view.spinner_canvas_image = self.view.spinner_canvas.create_image(50, 50, image=frame)
        else:
            self.view.spinner_canvas.itemconfig(self.view.spinner_canvas_image, image=frame)

        self.view.spinner_frame = (self.view.spinner_frame + 1) % len(self.view.spinner_frames)
        self.root.after(100, self.animate_spinner)

    def show_spinner(self):
        self.view.spinner_canvas.place(relx=0.5, rely=0.8, anchor="center")
        if not self.view.spinner_running:
            self.view.spinner_running = True
            self.animate_spinner()
        self.root.update()
    
    def hide_spinner(self):
        self.view.spinner_canvas.place_forget()
        self.view.spinner_running = False
        self.root.update()

    def load_drive_path(self):
        drive_path_file = self.model.get_user_data_path("drive_path.txt")   

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
        drive_path_file = self.model.get_user_data_path("drive_path.txt")   

        if drive_path:
            with open(drive_path_file, "w") as f:
                f.write(drive_path)
            self.drive = drive_path
            self.view.drive_label.config(text=f"Drive: {self.drive}")
            messagebox.showinfo("Drive Updated", "Shared drive path updated successfully!")

    def prompt_for_drive(self):
        messagebox.showinfo(
            "Select Drive Folder",
            "No drive selected.\n\nPlease choose your Google Drive shared folder before proceeding."
        )
