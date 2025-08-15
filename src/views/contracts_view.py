import tkinter as tk

from models.main_model import MainModel

class ContractsView(tk.Frame):
    def __init__(self, root, controller, model: MainModel, bg_color):
        super().__init__(root)
        self.root = root
        self.bg_color = bg_color
        self.configure(bg=bg_color)
        self.model = model
        self.controller = controller
