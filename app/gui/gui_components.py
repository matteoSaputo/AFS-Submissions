import tkinter as tk

BG_COLOR = "#f7f7f7"
DND_BG_COLOR = "#f0f0f0"

def create_title_label(app):
    title_label = tk.Label(
        app.root, 
        text="Upload AFS Application", 
        font=("Segoe UI", 18, "bold"), 
        bg=BG_COLOR
    )
    title_label.pack(pady=(30, 20))
    return title_label
