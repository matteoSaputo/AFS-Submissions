import tkinter as tk
import os
from tkinter import messagebox

def update_file_display(app):
    def limit_file_name(file, limit=50):
        name, extension = os.path.splitext(file)
        if len(file) > limit:
            return f"{name[:limit]}...{extension}"
        return file

    for widget in app.scroll_frame.winfo_children():
        widget.destroy()

    if not app.uploaded_files:
        hide_file_list_frame(app)
        return
    show_file_list_frame(app)

    for file in app.uploaded_files:
        row = tk.Frame(app.scroll_frame, bg=app.dnd_bg_color)
        row.pack(fill="x", padx=4, pady=2)

        label = tk.Button(row, text=limit_file_name(os.path.basename(file)), bg=app.dnd_bg_color, anchor="w")
        label.pack(side="left", fill="x", expand=True)

        btn = tk.Button(row, 
            text="❌", 
            command=lambda f=file: delete_uploaded_file(app, f),
            bg="#eb4034",
            fg="white",
            padx=6
        )

        btn.pack(side="right", padx=5)
        
    def make_scrollable_for_file_list(widget):
        if not widget:
            return
        if not app.scrollbar.winfo_ismapped():
            widget.unbind("<MouseWheel>")
        else:
            widget.bind(
                "<MouseWheel>",
                lambda event: app.scroll_canvas.yview_scroll(int(-1 * (event.delta/120)), "units") 
            )
        for w in widget.winfo_children():
            make_scrollable_for_file_list(w)
    make_scrollable_for_file_list(app.drop_frame)        

def delete_uploaded_file(app, file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        app.uploaded_files.remove(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete file {file_path}: {e}")
        
    if file_path == app.selected_application_file:
        app.selected_application_file = None
        clean_uploads_folder()
        reset_folder_UI()
        
    update_file_display(app)

def reset_folder_UI(app):
    app.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
    app.uploaded_files = []
    app.match_label.config(text="")
    app.confirm_btn.config(state=tk.DISABLED)
    app.new_folder_btn.config(state=tk.DISABLED)
    update_file_display(app)

def show_file_list_frame(app):
    app.upload_btn.place_forget()
    row_height = 30
    visible_rows = min(len(app.uploaded_files)+1, app.max_visible_rows)
    actual_height = row_height * visible_rows
    max_height = row_height * app.max_visible_rows
    relheight = actual_height / max_height - 0.02

    app.scroll_canvas.place(relx=0.02, rely=0.02, relwidth=0.9, relheight=relheight)
    app.scroll_frame.config(height=relheight)
    
    if len(app.uploaded_files)-1 > app.max_visible_rows:
        app.scrollbar.place(relx=0.92, rely=0.02, relheight=relheight)
    else:
        app.scrollbar.place_forget()

def hide_file_list_frame(app):    
    app.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
    app.scroll_canvas.place_forget()
    app.scrollbar.place_forget()