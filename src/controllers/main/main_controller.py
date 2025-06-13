import tkinter as tk
from controllers.submissions.submissions_controller import SubmissionsController
from models.main.main_model import MainModel
from views.main.footer import Footer
from views.main.main_view import MainView
from views.main.nav_bar import NavigationBar

BG_COLOR = "#f7f7f7"
DND_BG_COLOR = "#f0f0f0"
# FOOTER_BG_COLOR = "#474545"
FOOTER_BG_COLOR = "#387097"
NAVBAR_BG_COLOR = FOOTER_BG_COLOR

# BG_COLOR = "#ce5555"
# SUB_COLOR = "#EB88AE"

class MainController:
    def __init__(self, root):        
        self.model = MainModel()

        self.navbar = NavigationBar(root, NAVBAR_BG_COLOR)
        self.navbar.pack(fill="both", side='top')
        # self.navbar_place_buttons_evenly(self.navbar.btns)

        self.view = MainView(root, BG_COLOR)
        self.view.pack(fill='x')

        self.submissions_controller = SubmissionsController(self.view, BG_COLOR, DND_BG_COLOR)
        self.submissions_view = self.submissions_controller.view
        
        self.current_view = self.submissions_view
        self.display_submissions_view()

        self.footer = Footer(root, self.model.version, FOOTER_BG_COLOR)
        self.footer.pack(fill='x', side='bottom')

    def navbar_place_buttons_evenly(self, btns: list[tk.Button]):
        num_btns = len(btns)
        for btn in btns:
            btn.place(relheight=1.0, relwidth=0.25)

    def display_submissions_view(self):
        self.current_view.place_forget()
        self.submissions_view.pack(pady=10)
        self.current_view = self.submissions_view