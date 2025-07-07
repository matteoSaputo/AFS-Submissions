import time
import tkinter as tk
from tkinter import filedialog, messagebox

import os
import threading
import re

# Import model and view
from controllers.services.submissions_service import SubmissionService
from models.submissions.submissions_model import SubmissionsModel
from views.submissions.submissions_view import SubmissionsView

# --- Global constants ---
UPLOAD_DIR = "data/uploads"

# --- Main application controller ---
class SubmissionsController:
    def __init__(self, root, BG_COLOR, DND_BG_COLOR):
        self.root = root

        self.model = SubmissionsModel(UPLOAD_DIR)
        self.service = SubmissionService(self.model)

        self.bg_color = BG_COLOR
        self.dnd_bg_color = DND_BG_COLOR

        self.model.drive = self.load_drive_path()

        self.view = SubmissionsView(self, self.model, root)

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
        for widget in self.view.scroll_frame.winfo_children():
            widget.destroy()

        if not self.model.uploaded_files:
            self.hide_file_list_frame()
            return
        self.show_file_list_frame()

        for file in self.model.uploaded_files:
            row = tk.Frame(self.view.scroll_frame, bg=self.dnd_bg_color)
            row.pack(fill="x", padx=4, pady=2)

            label = tk.Button(row, text=self.service.limit_file_name(os.path.basename(file)), bg=self.dnd_bg_color, anchor="w")
            label.pack(side="left", fill="x", expand=True)

            btn = tk.Button(row, 
                text="❌", 
                command=lambda f=file: self.delete_file(f),
                bg=self.dnd_bg_color,
                fg="black",
                padx=6
            )

            if file == self.model.selected_application_file:
                label.config(bg='#bfbfbf')

            btn.pack(side="right", padx=5)
        
        self.make_scrollable_for_file_list(self.view.drop_frame)        

    def make_scrollable_for_file_list(self, widget: tk.Widget):
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
            self.make_scrollable_for_file_list(w)
        
    def delete_file(self, file_path):
        self.service.delete_file(file_path)  
        if self.model.selected_application_file == None:
            self.reset_folder_UI()      
        self.update_file_display()

    def process(self, file_list):          
        self.service.handle_files(file_list)
        self.update_file_display()

        if not self.model.selected_application_file:
            self.hide_spinner()
            return
        
        self.start_submission()

    def handle_files(self, file_list):
        self.show_spinner()
        threading.Thread(target=lambda: self.process(file_list)).start()

    def start_submission(self):
        # try:
            if not self.model.full_package:
                self.service.prepare_submission()
            if self.model.full_package:
                #start submission for full package
                self.service.prepare_full_packages()
                self.model.full_package = False
                self.model.clean_uploads()
                self.update_file_display()
                full_packages = os.listdir(self.model.full_packages_folder)
                statements_folder = filedialog.askdirectory(title="Select Folder for full packages bank statements")
                for csv in full_packages:
                    path = os.path.join(self.model.full_packages_folder, csv)
                    files = [path]
                    if statements_folder:
                        name = os.path.splitext(csv)[0]
                        statements = os.path.abspath(os.path.join(statements_folder, name))
                        def clean_path(path):
                            return re.sub(r'[\xa0\u200b]', '', path).strip()
                        statements = clean_path(statements)
                        for f in os.listdir(statements):
                            statement_path = os.path.abspath(os.path.join(statements_folder, f"{os.path.splitext(csv)[0].strip()}/{f}"))
                            print(statement_path)
                            files.append(statement_path)
                    self.process(files)
                    self.finalize_submission(use_existing=False)
                    os.remove(path)
                    print(path)
                    while self.model.selected_application_file:
                        time.sleep(0.1)
                return

            if self.model.matched_folder:
                self.view.match_label.config(
                    text=f"Matched Folder:\n{self.model.matched_folder}\n\nBusiness Name:\n{self.model.bus_name}\n\nMatch Score: {self.model.match_score}%"
                )
            else:
                self.view.match_label.config(text="No match found.\nWill create new folder.")

            self.view.title_label.pack_forget()
            self.view.change_drive_btn.pack_forget()
            self.view.drive_label.pack_forget()

            self.view.match_label.pack(pady=20)
            self.view.folder_button_frame.pack(pady=10)

        # except Exception as e:
        #     messagebox.showerror("Error", str(e))
            
        # finally:
        #     self.hide_spinner()

    def confirm_folder(self):
        self.finalize_submission(use_existing=True)

    def create_new_folder(self):
        self.finalize_submission(use_existing=False)

    def finalize_submission(self, use_existing):
        # try:
            self.service.finalize_submission(use_existing)
            # messagebox.showinfo("Success", "Submission processed successfully!")
            self.reset_folder_UI()
        # except Exception as e:
        #     messagebox.showerror("Error", f"Failed to process: {str(e)}")

    def reset_folder_UI(self):
        self.view.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
        self.service.reset_model_state()
        self.view.match_label.config(text="")
        self.view.drop_frame.pack_forget()
        self.view.title_label.pack(side='top', pady=(30, 20))
        self.view.change_drive_btn.pack(side='top', pady=(0, 10))
        self.view.drive_label.pack(side='top', pady=(0, 20))
        self.view.drop_frame.pack(side="top", pady=10)
        self.view.match_label.pack_forget()
        self.view.folder_button_frame.pack_forget()
        self.update_file_display()

    def show_file_list_frame(self):
        self.view.upload_btn.place_forget()
        row_height = 30
        visible_rows = min(len(self.model.uploaded_files)+1, self.view.max_visible_rows)
        actual_height = row_height * visible_rows
        max_height = row_height * self.view.max_visible_rows
        relheight = actual_height / max_height - 0.02

        self.view.scroll_canvas.place(relx=0.02, rely=0.02, relwidth=0.9, relheight=relheight)
        self.view.scroll_frame.config(height=relheight)
        
        if len(self.model.uploaded_files)-1 > self.view.max_visible_rows:
            self.view.scrollbar.place(relx=0.92, rely=0.02, relheight=relheight)
        else:
            self.view.scrollbar.place_forget()
        
        self.view.clear_files_btn.pack(side="bottom", pady=10)

    def hide_file_list_frame(self):    
        self.view.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
        self.view.clear_files_btn.pack_forget()
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
        self.view.spinner_canvas.pack(side="bottom")
        if not self.view.spinner_running:
            self.view.spinner_running = True
            self.animate_spinner()
        self.root.update()
    
    def hide_spinner(self):
        self.view.spinner_canvas.pack_forget()
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
            self.model.drive = drive_path
            self.view.drive_label.config(text=f"Drive: {self.model.drive}")
            messagebox.showinfo("Drive Updated", "Shared drive path updated successfully!")

    def prompt_for_drive(self):
        messagebox.showinfo(
            "Select Drive Folder",
            "No drive selected.\n\nPlease choose your Google Drive shared folder before proceeding."
        )
