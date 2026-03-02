"""
Footer: Application footer displaying version information.

Shows the current version of the application at the bottom of the window.
"""

import tkinter as tk

class Footer(tk.Frame):
    """Footer frame for displaying version info.

    Parameters
    ----------
    root : tk.Widget
        Parent widget for the footer.
    version : str
        Application version string.
    bg_color : str
        Background color for the footer.
    """

    def __init__(self, root, version, bg_color):
        """Initialize the Footer frame and display the version label.

        Parameters
        ----------
        root : tk.Widget
            Parent widget for the footer.
        version : str
            Application version string.
        bg_color : str
            Background color for the footer.
        """
        super().__init__(root)
        self.version = version
        self.bg_color = bg_color

        self.config(bg=bg_color)

        self.version_label = tk.Label(
            self,
            text=f"Version {self.version}",
            font=("Courier", 13, "bold"),
            fg="black",
            bg=self.bg_color
        )
        self.version_label.pack(side="top", pady=5)