import tkinter as tk
import os

from PIL import Image, ImageTk

from models.main_model import MainModel

class EmailView(tk.Frame):
    def __init__(self, root, model: MainModel, bg_color):
        super().__init__(root)
        self.root = root
        self.bg_color = bg_color
        self.configure(bg=bg_color)
        self.model = model

        self.label = tk.Label(
            self,
            text="Email Related Features To Be Implemented\nConsult the Senior Software Engineer Matteo Saputo for Development Progress\nFor now Enjoy Some Complementary Kitty Pics :)",
            font=("Courier", 13, "bold"),
            bg = self.bg_color
        )
        self.label.pack()

        self.cat_frame = tk.Frame(self, bg=bg_color)
        self.cat_frame.pack()
        self.cat_pics = []
        cat_folder = "assets/cats"
        columns = 3

        for idx, kitty_pic in enumerate(os.listdir(self.model.resource_path(cat_folder))):
            img_path = os.path.join(self.model.resource_path(cat_folder), kitty_pic)
            img = Image.open(img_path)
            img.thumbnail((150, 150))
            image_tk = ImageTk.PhotoImage(img)

            label = tk.Label(self.cat_frame, image=image_tk, bg=bg_color)
            self.cat_pics.append(image_tk)

            row = idx // columns
            col = idx % columns
            label.grid(row=row, column=col, padx=10, pady=10)