"""
main_controller: Main application controller for AFS Submissions Tool.

Initializes the main model, navigation bar, views, and sub-controllers for submissions, contracts, and email features.
"""

import tkinter as tk
from tkinter import filedialog, messagebox

from controllers.submissions_controller import SubmissionsController
from controllers.contracts_controller import ContractsController
from controllers.email_controller import EmailController

from models.main_model import MainModel

from views.components.footer import Footer
from views.main_view import MainView
from views.components.nav_bar import NavigationBar

BG_COLOR = "#f7f7f7"
DND_BG_COLOR = "#f0f0f0"
FOOTER_BG_COLOR = "#575757"
NAVBAR_BG_COLOR = FOOTER_BG_COLOR

SUB_COLOR = BG_COLOR

class MainController:
    """Main application controller.

    Parameters
    ----------
    root : tk.Tk
        The main Tkinter root window.
    """
    def __init__(self, root):        
        """Initialize the MainController and set up all views and sub-controllers.

        Parameters
        ----------
        root : tk.Tk
            The main Tkinter root window.
        """
        self.root = root

        self.model = MainModel()
        self.model.drive = self.load_drive_path()

        self.navbar = NavigationBar(root, NAVBAR_BG_COLOR)
        self.navbar.pack(fill="both", side='top')

        self.view = MainView(root, BG_COLOR)
        self.view.pack(fill='x')

        self.submissions_controller = SubmissionsController(self.view, BG_COLOR, DND_BG_COLOR)
        self.submissions_view = self.submissions_controller.view
        self.submissions_btn = self.navbar.submissions_btn
        self.bind_navbar_btn(self.submissions_btn, self.submissions_view)

        self.contracts_controller = ContractsController(self.view, BG_COLOR, DND_BG_COLOR)
        self.contracts_view = self.contracts_controller.view
        self.contracts_btn = self.navbar.contracts_btn
        self.bind_navbar_btn(self.contracts_btn, self.contracts_view)

        self.email_controller = EmailController(self.view, BG_COLOR)
        self.email_view = self.email_controller.view
        self.email_btn = self.navbar.email_btn
        self.bind_navbar_btn(self.email_btn, self.email_view)
        
        self.current_view = self.submissions_view
        self.submissions_btn.config(state=tk.DISABLED)
        self.display_view(self.submissions_view)

        self.footer = Footer(root, self.model.version, FOOTER_BG_COLOR)
        self.footer.pack(fill='x', side='bottom')

    def display_view(self, view: tk.Frame):
        """Display the given view, hiding the current one.

        Parameters
        ----------
        view : tk.Frame
            The view to display.
        """
        self.current_view.pack_forget()
        self.current_view = view
        self.current_view.pack(pady=10)

    def bind_navbar_btn(self, btn: tk.Button, view: tk.Frame):
        """Bind a navigation bar button to display a specific view.

        Parameters
        ----------
        btn : tk.Button
            The navigation button to bind.
        view : tk.Frame
            The view to display when the button is clicked.
        """
        def display():
            for button in self.navbar.btns:
                button.config(state=tk.NORMAL)                
            btn.config(state=tk.DISABLED)
            self.display_view(view)
        btn.config(command=display)

    def load_drive_path(self):
        """Prompt the user to select a drive folder if not already set.

        Returns
        -------
        str
            The selected drive path.
        """
        if self.model.drive:
            return self.model.drive

        drive_path_file = self.model.get_user_data_path("drive_path.txt") 

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
    
    def prompt_for_drive(self):
        """Show an info dialog prompting the user to select a drive folder."""
        messagebox.showinfo(
            "Select Drive Folder",
            "No drive selected.\n\nPlease choose your Google Drive shared folder before proceeding."
        )