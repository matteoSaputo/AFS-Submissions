import os
import tkinter as tk

from controllers.contracts_service import ContracstService
from controllers.submissions_controller import SubmissionsController
from models.contracts_model import ContractsModel
from views.contracts_view import ContractsView

from models.utils.afs_parser import extract_from_pdf

class ContractsController(SubmissionsController):
    def __init__(self, root, bg_color, dnd_bg_color):
        self.root = root
        self.bg_color = bg_color
        self.dnd_bg_color = dnd_bg_color

        self.model = ContractsModel()
        self.service = ContracstService(self.model)

        self.view = ContractsView(root, self, self.model, self.bg_color)
    
    def reset_folder_UI(self):
        self.service.reset_model_state()
        self.view.folder_match_frame.match_label.config(text="")
        self.view.drop_frame.pack_forget()
        self.view.options.pack_forget()
        self.view.title_label.pack(side='top', pady=(30, 20))
        self.view.change_drive_btn.pack(side='top')
        self.view.options.pack(padx=16, pady=(8, 12))
        self.view.drop_frame.pack(side="top", pady=10)
        self.view.folder_match_frame.folder_button_frame.pack_forget()
        self.view.folder_match_frame.pack_forget()
        self.view.drop_frame.update_file_display()
    
