"""
NavigationBar: Top navigation bar for AFS Submissions Tool.

Provides buttons for switching between Submissions, Contracts, and Email views.
"""

import tkinter as tk

class NavigationBar(tk.Frame):
    """Navigation bar frame with view-switching buttons.

    Parameters
    ----------
    root : tk.Widget
        Parent widget for the navigation bar.
    bg_color : str
        Background color for the navigation bar and buttons.
    """

    def __init__(self, root, bg_color):
        """Initialize the NavigationBar and its buttons.

        Parameters
        ----------
        root : tk.Widget
            Parent widget for the navigation bar.
        bg_color : str
            Background color for the navigation bar and buttons.
        """
        super().__init__(root)
        
        self.bg_color = bg_color
        self.btns = []
        self.config(bg=bg_color, height=140)

        self.btns_label = tk.Label(
            self,
            text="Label",
            bg=self.bg_color
        )
        self.btns_label.place(relheight=1.0, relwidth=1.0)

        self.submissions_btn = tk.Button(
            self.btns_label,
            text="Submissions",
            font=("Courier", 13, "bold"),
            fg="black",
            bg=bg_color,
        )
        self.btns.append(self.submissions_btn)

        self.contracts_btn = tk.Button(
            self.btns_label,
            text=" Contracts ",       
            font=("Courier", 13, "bold"),
            fg="black",
            bg=bg_color,
        )
        self.btns.append(self.contracts_btn)

        self.email_btn = tk.Button(
            self.btns_label,
            text="   Email   ",
            font=("Courier", 13, "bold"),
            fg="black",
            bg=bg_color,
        )
        self.btns.append(self.email_btn)

        self.navbar_place_buttons()

    def navbar_place_buttons(self):
        """Pack all navigation buttons into the navigation bar."""
        for btn in self.btns:
            btn.pack(side="left", expand=True, fill="both")