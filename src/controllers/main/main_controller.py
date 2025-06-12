from controllers.submissions.submissions_controller import SubmissionsController
from models.main.main_model import MainModel
from views.main.footer_view import Footer
from views.main.main_view import MainView

BG_COLOR = "#f7f7f7"
DND_BG_COLOR = "#f0f0f0"
FOOTER_BG_COLOR = "#474545"

class MainController:
    def __init__(self, root):        
        self.model = MainModel()
        
        self.view = MainView(root, BG_COLOR)
        self.view.pack(expand=True)

        self.submissions_controller = SubmissionsController(self.view, BG_COLOR, DND_BG_COLOR)
        self.submissions_view = self.submissions_controller.view
        
        self.current_view = self.submissions_view
        self.display_submissions_view()

        self.footer = Footer(root, self.model.version, FOOTER_BG_COLOR)
        self.footer.pack(fill='x', side='bottom')

    def display_submissions_view(self):
        self.current_view.place_forget()
        self.submissions_view.pack(side='bottom')
        self.current_view = self.submissions_view