import tkinter as tk

from models.contracts.contracts_model import ContractsModel
from views.contracts.contracts_view import ContractsView

class ContractsController:
    def __init__(self, root, bg_color):
        self.root = root
        self.bg_color = bg_color
        
        self.model = ContractsModel()

        self.view = ContractsView(root, self.model, bg_color)
