"""
FolderMatchFrame: UI for matching and confirming folders.

Provides buttons to confirm or create a new folder for uploads.
"""

import tkinter as tk

class FolderMatchFrame(tk.Frame):
    """Frame for folder matching and confirmation.

    Parameters
    ----------
    root : tk.Widget
        Parent widget for the frame.
    bg : str
        Background color for the frame.
    new_folder_handler : Callable
        Function to call when creating a new folder.
    confirm_folder_handler : Callable
        Function to call when confirming folder selection.
    """

    def __init__(self, root, bg, new_folder_handler, confirm_folder_handler):
        """Initialize the FolderMatchFrame and its UI components.

        Parameters
        ----------
        root : tk.Widget
            Parent widget for the frame.
        bg : str
            Background color for the frame.
        new_folder_handler : Callable
            Function to call when creating a new folder.
        confirm_folder_handler : Callable
            Function to call when confirming folder selection.
        """
        super().__init__(root)
        self.new_folder_handler = new_folder_handler
        self.confirm_folder_handler = confirm_folder_handler
        self.bg_color = bg
        self.configure(bg=self.bg_color)

        self.match_label = tk.Label(
            self,  
            text="", 
            font=("Segoe UI", 12), 
            bg=self.bg_color
        )

        self.folder_button_frame = tk.Frame(self, bg=self.bg_color)
        # self.folder_button_frame.pack()

        self.confirm_btn = tk.Button(
            self.folder_button_frame, 
            text="✅ Use This Folder", 
            font=("Segoe UI", 12), 
            command=self.confirm_folder_handler, 
            bg="#28a745", 
            fg="white", 
            width=20
        )
        self.confirm_btn.pack(side="left", padx=5)

        self.new_folder_btn = tk.Button(
            self.folder_button_frame, 
            text="❌ Create New Folder", 
            font=("Segoe UI", 12), 
            command=self.new_folder_handler, 
            bg="#dc3545", 
            fg="white", 
            width=20
        )
        self.new_folder_btn.pack(side="left", padx=15)