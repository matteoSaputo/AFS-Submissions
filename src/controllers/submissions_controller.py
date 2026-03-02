"""
submissions_controller: Controller for managing AFS submissions.

Handles file uploads, drag-and-drop events, file deletion, and interaction between the submissions model and view.
"""

import time
import tkinter as tk
from tkinter import filedialog, messagebox

import os
import threading
import re

# Import model and view
from models.services.submissions_service import SubmissionService
from models.submissions_model import SubmissionsModel
from views.submissions_view import SubmissionsView

# --- Main application controller ---
class SubmissionsController:
    """Controller for AFS submissions.

    Parameters
    ----------
    root : tk.Tk
        The main Tkinter root window.
    BG_COLOR : str
        Background color for the view.
    DND_BG_COLOR : str
        Drag-and-drop background color for the view.
    """

    def __init__(self, root: tk.Tk, BG_COLOR, DND_BG_COLOR):
        """Initialize the SubmissionsController and set up model, service, and view.

        Parameters
        ----------
        root : tk.Tk
            The main Tkinter root window.
        BG_COLOR : str
            Background color for the view.
        DND_BG_COLOR : str
            Drag-and-drop background color for the view.
        """
        self.root = root

        self.model = SubmissionsModel()
        self.service = SubmissionService(self.model)

        self.bg_color = BG_COLOR
        self.dnd_bg_color = DND_BG_COLOR

        self.view = SubmissionsView(self, self.model, root)

    def upload_pdf(self):
        """Open a file dialog to select PDF files and handle them."""
        file_paths = list(filedialog.askopenfilenames())
        if not file_paths:
            return
        self.handle_files(file_paths)

    def handle_drop(self, event):
        """Handle files dropped onto the drop frame."""
        self.view.drop_frame.config(bg="#d0f0d0")
        dropped_files = self.root.tk.splitlist(event.data)
        pdf_files = [os.path.abspath(f.strip('{}')) for f in dropped_files]
        self.handle_files(pdf_files)
        self.view.drop_frame.config(bg=self.dnd_bg_color)
        
    def delete_file(self, file_path):
        """Delete a file from the uploaded files list and update the UI."""
        self.service.delete_file(file_path)  
        if self.model.selected_application_file == None:
            self.reset_folder_UI()      
        self.view.drop_frame.update_file_display()

    def process(self, file_list):          
        """Process a list of files, updating the UI and handling full packages."""
        self.service.handle_files(file_list)
        self.view.drop_frame.update_file_display()

        if not self.model.selected_application_file:
            self.view.spinner.hide_spinner()
            return
        
        self.start_submission()

    def handle_files(self, file_list):
        """Show spinner and process files in a separate thread."""
        self.view.spinner.show_spinner()
        threading.Thread(target=lambda: self.process(file_list)).start()

    def start_submission(self):
        """Start the submission process, handling full packages and folder matching."""
        # try:
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
            self.view.folder_match_frame.match_label.config(
                text=f"Matched Folder:\n{self.model.matched_folder}\n\nBusiness Name:\n{self.model.bus_name}\n\nMatch Score: {self.model.match_score}%"
            )
        else:
            self.view.folder_match_frame.match_label.config(text="No match found.\nWill create new folder.")

        self.view.title_label.pack_forget()
        self.view.change_drive_btn.pack_forget()

        self.view.folder_match_frame.match_label.pack(pady=20)
        self.view.folder_match_frame.pack(pady=10)
        self.view.folder_match_frame.folder_button_frame.pack(pady=20)


        # except Exception as e:
        #     messagebox.showerror("Error", str(e))
            
        # finally:
        #     self.view.spinner.hide_spinner()

    def confirm_folder(self):
        """Finalize the submission using the matched folder."""
        self.finalize_submission(use_existing=True)

    def create_new_folder(self):
        """Finalize the submission by creating a new folder."""
        self.finalize_submission(use_existing=False)

    def finalize_submission(self, use_existing):
        """Finalize the submission and show a success or error message.

        Parameters
        ----------
        use_existing : bool
            Whether to use the matched folder or create a new one.
        """
        # try:
        self.service.finalize_submission(use_existing)
        messagebox.showinfo("Success", "Submission processed successfully!")
        self.reset_folder_UI()
        # except Exception as e:
        #     messagebox.showerror("Error", f"Failed to process: {str(e)}")

    def reset_folder_UI(self):
        """Reset the folder matching UI to its initial state."""
        self.service.reset_model_state()
        self.view.folder_match_frame.match_label.config(text="")
        for w in self.view.winfo_children():
            w.pack_forget()
        self.view.title_label.pack(side='top', pady=(30, 20))
        self.view.change_drive_btn.pack(side='top')
        self.view.drop_frame.pack(side="top", pady=10)
        self.view.drop_frame.update_file_display()