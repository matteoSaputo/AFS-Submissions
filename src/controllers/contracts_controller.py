import os
import tkinter as tk

from models.contracts_model import ContractsModel
from views.contracts_view import ContractsView

from models.utils.afs_parser import extract_from_pdf

class ContractsController:
    def __init__(self, root, bg_color, dnd_bg_color):
        self.root = root
        self.bg_color = bg_color
        self.dnd_bg_color = dnd_bg_color

        self.model = ContractsModel()

        self.view = ContractsView(root, self, self.model, self.bg_color)

    def upload_pdf(self):
        print("uplaod")
        return
    
    def handle_drop(self, event):
        print("drop")
        print(event)
        dropped_files = self.root.tk.splitlist(event.data)
        pdf_files = [os.path.abspath(f.strip('{}')) for f in dropped_files]
        print(extract_from_pdf(pdf_files[0]))
        return
    
    def reset_folder_UI(self):
        print("reset")
        return
    
    def delete_file(self, file_path):
        print("delete")
        return
