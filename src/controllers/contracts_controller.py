"""
contracts_controller: Controller for managing contract submissions.

Handles contract data preparation, folder matching, and UI updates for contract-related features.
"""


from tkinter import messagebox

from models.services.contracts_service import ContracstService
from controllers.submissions_controller import SubmissionsController
from models.contracts_model import ContractsModel
from views.contracts_view import ContractsPageOne
from views.contracts_view_2 import ContractsPageTwo

class ContractsController(SubmissionsController):
    """Controller for contract submissions.

    Parameters
    ----------
    root : tk.Tk
        The main Tkinter root window.
    bg_color : str
        Background color for the view.
    dnd_bg_color : str
        Drag-and-drop background color for the view.
    """
    def __init__(self, root, bg_color, dnd_bg_color):
        """Initialize the ContractsController and set up model, service, and views.

        Parameters
        ----------
        root : tk.Tk
            The main Tkinter root window.
        bg_color : str
            Background color for the view.
        dnd_bg_color : str
            Drag-and-drop background color for the view.
        """
        self.root = root
        self.bg_color = bg_color
        self.dnd_bg_color = dnd_bg_color

        self.model = ContractsModel()
        self.service = ContracstService(self.model)

        self.view = ContractsPageOne(root, self, self.model, self.bg_color)
        self.view_2 = None

    def start_submission(self):
        """Start the contract submission process and update the UI."""
        try:
            self.service.prepare_submission()
            
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
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.view.spinner.hide_spinner()

    def finalize_submission(self, use_existing):
        """Finalize the contract submission and show the contract details page.

        Parameters
        ----------
        use_existing : bool
            Whether to use the matched folder or create a new one.
        """
        self.model.afs_data["Fee"] = self.view.fee_combo.get()
        self.model.afs_data["Frequency"] = self.view.freq_combo.get().lower()
        self.model.afs_data["Interest Rate"] = self.view.rate_combo.get()
        for w in self.view.winfo_children():
            w.pack_forget()
        self.view_2 = ContractsPageTwo(
            self.view,
            self,
            self.model,
            self.bg_color,
            finalize_handler=lambda: super(ContractsController, self).finalize_submission(use_existing),
            reset_ui_handler=self.reset_folder_UI
        ).pack(pady=20)
    
    def reset_folder_UI(self):
        """Reset the folder matching UI to its initial state for contracts."""
        self.service.reset_model_state()
        self.view.folder_match_frame.match_label.config(text="")
        for w in self.view.winfo_children():
            w.pack_forget()
        self.view.title_label.pack(side='top', pady=(30, 20))
        self.view.change_drive_btn.pack(side='top')
        self.view.options.pack(padx=16, pady=(8, 12))
        self.view.drop_frame.pack(side="top", pady=10)
        self.view.drop_frame.update_file_display()

