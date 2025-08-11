import tkinter as tk

from controllers.submissions.submissions_controller import SubmissionsController
from controllers.contracts.contracts_controller import ContractsController
from controllers.email.email_controller import EmailController

from models.main.main_model import MainModel

from views.main.footer import Footer
from views.main.main_view import MainView
from views.main.nav_bar import NavigationBar

BG_COLOR = "#f7f7f7"
DND_BG_COLOR = "#f0f0f0"
FOOTER_BG_COLOR = "#387097"
NAVBAR_BG_COLOR = FOOTER_BG_COLOR

SUB_COLOR = BG_COLOR

class MainController:
    def __init__(self, root):        
        self.model = MainModel()

        self.navbar = NavigationBar(root, NAVBAR_BG_COLOR)
        self.navbar.pack(fill="both", side='top')

        self.view = MainView(root, BG_COLOR)
        self.view.pack(fill='x')

        self.submissions_controller = SubmissionsController(self.view, BG_COLOR, DND_BG_COLOR)
        self.submissions_view = self.submissions_controller.view
        self.submissions_btn = self.navbar.submissions_btn
        self.bind_navbar_btn(self.submissions_btn, self.submissions_view)

        self.contracts_controller = ContractsController(self.view, BG_COLOR, DND_BG_COLOR)
        self.contracts_view = self.contracts_controller.view
        self.contracts_btn = self.navbar.contracts_btn
        self.bind_navbar_btn(self.contracts_btn, self.contracts_view)

        self.email_controller = EmailController(self.view, BG_COLOR)
        self.email_view = self.email_controller.view
        self.email_btn = self.navbar.email_btn
        self.bind_navbar_btn(self.email_btn, self.email_view)
        
        self.current_view = self.submissions_view
        self.submissions_btn.config(state=tk.DISABLED)
        self.display_view(self.submissions_view)

        self.footer = Footer(root, self.model.version, FOOTER_BG_COLOR)
        self.footer.pack(fill='x', side='bottom')

    def display_view(self, view: tk.Frame):
        self.current_view.pack_forget()
        self.current_view = view
        self.current_view.pack(pady=10)

    def bind_navbar_btn(self, btn: tk.Button, view: tk.Frame):
        def display():
            for button in self.navbar.btns:
                button.config(state=tk.NORMAL)                
            btn.config(state=tk.DISABLED)
            self.display_view(view)
        btn.config(command=display)