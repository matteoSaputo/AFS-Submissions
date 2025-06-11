import tkinter as tk

class Footer(tk.Frame):
    def __init__(self, root, version, bg_color):
        super().__init__(root)
        self.version = version
        self.bg_color = bg_color

        self.config(bg=bg_color)

        self.version_label = tk.Label(
            self,
            text=f"Version: {self.version}",
            font=("Segoe UI", 13, "bold"),
            fg="black",
            bg=self.bg_color
        )
        self.version_label.pack(side="top", pady=10)