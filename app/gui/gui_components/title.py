import tkinter as tk

def create_title_label(app):
    title_label = tk.Label(
        app.root, 
        text="Upload AFS Application", 
        font=("Segoe UI", 18, "bold"), 
        bg=app.bg_color
    )
    title_label.pack(pady=(30, 20))
    return title_label
