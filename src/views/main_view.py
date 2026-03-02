"""
MainView: Main application window for AFS Submissions Tool.

Sets up the root Tkinter window, applies background color, and configures window geometry and title.
"""

import tkinter as tk

class MainView(tk.Frame):
    """Main application view frame.

    Parameters
    ----------
    root : tk.Tk
        The main Tkinter root window.
    bg_color : str
        Background color for the window and frame.
    """

    def __init__(self, root: tk.Tk, bg_color):
        """Initialize the MainView frame and configure the main window.

        Parameters
        ----------
        root : tk.Tk
            The main Tkinter root window.
        bg_color : str
            Background color for the window and frame.
        """
        super().__init__(root)

        self.root = root
        self.root.title("AFS Submission Tool")
        self.root.geometry("800x900")
        root.configure(bg=bg_color)    

        self.config(bg=bg_color)