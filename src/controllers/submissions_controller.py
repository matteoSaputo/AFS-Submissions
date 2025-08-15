import time
import tkinter as tk
from tkinter import filedialog, messagebox

import os
import threading
import re

# Import model and view
from controllers.submissions_service import SubmissionService
from models.submissions_model import SubmissionsModel
from views.submissions_view import SubmissionsView

# --- Main application controller ---
class SubmissionsController:
    def __init__(self, root: tk.Tk, BG_COLOR, DND_BG_COLOR):
        self.root = root

        self.model = SubmissionsModel()
        self.service = SubmissionService(self.model)

        self.bg_color = BG_COLOR
        self.dnd_bg_color = DND_BG_COLOR

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
        
    def delete_file(self, file_path):
        self.service.delete_file(file_path)  
        if self.model.selected_application_file == None:
            self.reset_folder_UI()      
        # self.update_file_display()
        self.view.drop_frame.update_file_display()

    def process(self, file_list):          
        self.service.handle_files(file_list)
        # self.update_file_display()
        self.view.drop_frame.update_file_display()

        if not self.model.selected_application_file:
            self.hide_spinner()
            return
        
        self.start_submission()

    def handle_files(self, file_list):
        self.show_spinner()
        threading.Thread(target=lambda: self.process(file_list)).start()

    def start_submission(self):
        try:
            if not self.model.full_package:
                self.service.prepare_submission()
            if self.model.full_package: # this is a mess lol
                #start submission for full package
                self.service.prepare_full_packages()
                self.model.full_package = False
                self.model.clean_uploads()
                self.view.drop_frame.update_file_display()
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
            self.service.finalize_submission(use_existing)
            messagebox.showinfo("Success", "Submission processed successfully!")
            self.reset_folder_UI()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process: {str(e)}")

    def reset_folder_UI(self):
        self.service.reset_model_state()
        self.view.match_label.config(text="")
        self.view.drop_frame.pack_forget()
        self.view.title_label.pack(side='top', pady=(30, 20))
        self.view.change_drive_btn.pack(side='top', pady=(0, 10))
        self.view.drive_label.pack(side='top', pady=(0, 20))
        self.view.drop_frame.pack(side="top", pady=10)
        self.view.match_label.pack_forget() 
        self.view.folder_button_frame.pack_forget()
        self.view.drop_frame.update_file_display()

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

    def change_drive_path(self):
        drive_path = filedialog.askdirectory(title="Select New Shared Drive Root Folder")
        if self.model.change_drive_path(drive_path):
            self.view.drive_label.config(text=f"Drive: {self.model.drive}")
            messagebox.showinfo("Drive Updated", "Shared drive path updated successfully!")