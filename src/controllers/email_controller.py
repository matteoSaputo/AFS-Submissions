import tkinter as tk

from models.email_model import EmailModel
from views.email_view import EmailView

class EmailController:
    def __init__(self, root, bg_color):
        self.root = root
        self.bg_color = bg_color
        
        self.model = EmailModel()

        self.view = EmailView(root, self.model, bg_color)