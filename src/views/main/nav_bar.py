import tkinter as tk

class NavigationBar(tk.Frame):
    def __init__(self, root, bg_color):
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
            font=("Segoe UI", 13, "bold"),
            fg="black",
            bg=bg_color,
        )
        # self.submissions_btn.place(relheight=1.0)
        self.submissions_btn.pack(side="left", expand=True, fill="both")
        self.btns.append(self.submissions_btn)

        self.contracts_btn = tk.Button(
            self.btns_label,
            text=" Contracts ",       
            font=("Segoe UI", 13, "bold"),
            fg="black",
            bg=bg_color,
        )
        # self.contracts_btn.place(relheight=1.0)
        self.contracts_btn.pack(side="left", expand=True, fill="both")
        self.btns.append(self.contracts_btn)

        self.email_btn = tk.Button(
            self.btns_label,
            text="   Email   ",
            font=("Segoe UI", 13, "bold"),
            fg="black",
            bg=bg_color,
        )
        # self.email_btn.place(relheight=1.0)
        self.email_btn.pack(side="left", expand=True, fill="both")
        self.btns.append(self.email_btn)

