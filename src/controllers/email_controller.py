"""
email_controller: Controller for managing email-related features.

Initializes the email model and view for email-related UI components.
"""

import tkinter as tk

from models.email_model import EmailModel
from views.email_view import EmailView

class EmailController:
    """Controller for email-related features.

    Parameters
    ----------
    root : tk.Tk
        The main Tkinter root window.
    bg_color : str
        Background color for the view.
    """

    def __init__(self, root, bg_color):
        """Initialize the EmailController and set up the model and view.

        Parameters
        ----------
        root : tk.Tk
            The main Tkinter root window.
        bg_color : str
            Background color for the view.
        """
        self.root = root
        self.bg_color = bg_color
        
        self.model = EmailModel()

        self.view = EmailView(root, self.model, bg_color)