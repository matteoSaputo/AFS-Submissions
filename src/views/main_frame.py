import tkinter as tk

from controllers.submissions_controller import SubmissionsController

BG_COLOR = "#f7f7f7"
DND_BG_COLOR = "#f0f0f0"

class MainFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.root.title("AFS Submission Tool")
        self.root.geometry("800x800")

        self.configure(bg=BG_COLOR)

        self.submissions_controller = SubmissionsController(root, BG_COLOR, DND_BG_COLOR)
        self.submissions_view = self.submissions_controller.view

        self.current_view = self.submissions_view
        self.display_submissions_view()

        self.place(relheight=1.0, relwidth=1.0)

    def display_submissions_view(self):
        self.current_view.place_forget()
        self.submissions_view.place(relheight=1.0, relwidth=1.0)
        self.current_view = self.submissions_view
        