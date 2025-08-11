import tkinter as tk
import os

from PIL import Image, ImageTk

from models.main.main_model import MainModel
from views.submissions.submissions_view import SubmissionsView

class ContractsView(tk.Frame):
    def __init__(self, root, controller, model: MainModel, bg_color):
        super().__init__(root)
        self.root = root
        self.bg_color = bg_color
        self.configure(bg=bg_color)
        self.model = model
        self.controller = controller
