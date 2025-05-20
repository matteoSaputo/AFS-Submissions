from tkinter import filedialog, messagebox

import os
import shutil
import zipfile
import threading

from gui.gui_utils.conditional_rendering import reset_folder_UI, update_file_display
from modules.afs_parser import is_likely_application

def upload_pdf(app):
    file_paths = filedialog.askopenfilenames()
    if not file_paths:
        return
    handle_files(app, file_paths)

def handle_drop(app, event):
    app.drop_frame.config(bg="#d0f0d0")
    dropped_files = app.root.tk.splitlist(event.data)
    pdf_files = [os.path.abspath(f.strip('{}')) for f in dropped_files]
    handle_files(app, pdf_files)
    app.drop_frame.config(bg=app.dnd_bg_color)

def clean_uploads_folder(app):
    files_to_delete =[
        f for f in os.listdir(app.upload_dir) if f != "keep.txt"
    ]

    if not files_to_delete:
        return
        
    for file in files_to_delete:
        file_path = os.path.join(app.upload_dir, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. {e}")

# def update_file_display(app):
#     def limit_file_name(file, limit=50):
#         name, extension = os.path.splitext(file)
#         if len(file) > limit:
#             return f"{name[:limit]}...{extension}"
#         return file

#     for widget in app.scroll_frame.winfo_children():
#         widget.destroy()

#     if not app.uploaded_files:
#         app.hide_file_list_frame()
#         return
#     app.show_file_list_frame()

#     for file in app.uploaded_files:
#         row = tk.Frame(app.scroll_frame, bg=app.dnd_bg_color)
#         row.pack(fill="x", padx=4, pady=2)

#         label = tk.Button(row, text=limit_file_name(os.path.basename(file)), bg=app.dnd_bg_color, anchor="w")
#         label.pack(side="left", fill="x", expand=True)

#         btn = tk.Button(row, 
#             text="❌", 
#             command=lambda f=file: delete_uploaded_file(f),
#             bg="#eb4034",
#             fg="white",
#             padx=6
#         )

#         btn.pack(side="right", padx=5)
        
#     def make_scrollable_for_file_list(widget):
#         if not widget:
#             return
#         if not app.scrollbar.winfo_ismapped():
#             widget.unbind("<MouseWheel>")
#         else:
#             widget.bind(
#                 "<MouseWheel>",
#                 lambda event: app.scroll_canvas.yview_scroll(int(-1 * (event.delta/120)), "units") 
#             )
#         for w in widget.winfo_children():
#             make_scrollable_for_file_list(w)
#     make_scrollable_for_file_list(app.drop_frame)        

# def delete_uploaded_file(app, file_path):
#     try:
#         if os.path.exists(file_path):
#             os.remove(file_path)
#         app.uploaded_files.remove(file_path)
#     except Exception as e:
#         messagebox.showerror("Error", f"Failed to delete file {file_path}: {e}")
        
#     if file_path == app.selected_application_file:
#         app.selected_application_file = None
#         app.clean_uploads_folder()
#         app.reset_folder_UI()
        
#     app.update_file_display()

def extract_zip(zip_path):
    extracted = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip:
            zip.extractall(os.path.dirname(zip_path))
            for name in zip.namelist():
                extracted_path = os.path.join(os.path.dirname(zip_path), name)
                extracted.append(extracted_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract {os.path.basename(zip_path)}")
    return extracted

def handle_files(app, file_list):
    app.show_spinner()

    def process():          
        extracted_files = []

        for original_path in file_list:
            if original_path.lower().endswith(".zip"):
                file_list.extend(extract_zip(original_path))
                continue
            extracted_files.append(original_path)

        likely_application = ""
        for file in extracted_files:
            if is_likely_application(file):
                likely_application = file
                    
        if likely_application:
            clean_uploads_folder(app)
            reset_folder_UI(app)

        for file in extracted_files:
            filename = os.path.basename(file)
            dest_path = os.path.join(app.upload_dir, filename)
            if not os.path.exists(dest_path):
                shutil.copy(file, dest_path)
            if filename == os.path.basename(likely_application):
                app.selected_application_file = dest_path
            app.uploaded_files.append(dest_path)

        update_file_display(app)

        if not likely_application:
            app.hide_spinner()
            return
            
        app.start_submission(app.selected_application_file)

    threading.Thread(target=process).start()