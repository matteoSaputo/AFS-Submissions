import tkinter as tk

class MainView(tk.Frame):
    def __init__(self, root: tk.Tk, bg_color):
        super().__init__(root)

        self.root = root
        self.root.title("AFS Submission Tool")
        self.root.geometry("800x800")
        root.configure(bg=bg_color)    

        self.configure(bg=bg_color)    