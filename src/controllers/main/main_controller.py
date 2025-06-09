from controllers.submissions.submissions_controller import SubmissionsController
from views.main.main_view import MainView

BG_COLOR = "#f7f7f7"
DND_BG_COLOR = "#f0f0f0"

class MainController:
    def __init__(self, root):        
        self.view = MainView(root, BG_COLOR)
        self.view.place(relheight=1.0, relwidth=1.0)

        self.submissions_controller = SubmissionsController(self.view, BG_COLOR, DND_BG_COLOR)
        self.submissions_view = self.submissions_controller.view
        
        self.current_view = self.submissions_view
        self.display_submissions_view()

    def display_submissions_view(self):
        self.current_view.place_forget()
        self.submissions_view.place(relheight=1.0, relwidth=1.0)
        self.current_view = self.submissions_view