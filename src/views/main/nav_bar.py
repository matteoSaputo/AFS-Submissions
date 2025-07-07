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
        for btn in self.btns:
            btn.pack(side="left", expand=True, fill="both")