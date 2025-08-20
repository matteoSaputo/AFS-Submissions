import threading
import tkinter as tk
from typing import Callable
from PIL import Image, ImageTk

class Spinner(tk.Canvas):
    def __init__(self, root, spinner_path, width, height, bg):
        # --- Spinner setup ---
        self.root = root
        self.spinner_path = spinner_path
        self.spinner_frames = []
        self.width = width
        self.height = height
        self.bg_color = bg
        self.spinner_canvas_image = None 
        self.spinner_running = False
        self.spinner_frame = 0

        img = Image.open(self.spinner_path)

        super().__init__(
            root,
            width=self.width,
            height=self.height,
            highlightthickness=0,
            bg=self.bg_color
        )

        # Load all frames
        try:
            while True:
                frame = ImageTk.PhotoImage(img.copy().convert('RGBA'))  # ensure transparency preserved
                self.spinner_frames.append(frame)
                img.seek(len(self.spinner_frames))  # move to next frame
        except EOFError:
            pass

    def animate_spinner(self):
        if not self.spinner_running:
            return

        frame = self.spinner_frames[self.spinner_frame]

        if self.spinner_canvas_image is None:
            self.spinner_canvas_image = self.create_image(50, 50, image=frame)
        else:
            self.itemconfig(self.spinner_canvas_image, image=frame)

        self.spinner_frame = (self.spinner_frame + 1) % len(self.spinner_frames)
        self.root.after(100, self.animate_spinner)

    def show_spinner(self):
        self.pack(side="bottom")
        if not self.spinner_running:
            self.spinner_running = True
            self.animate_spinner()
        self.root.update()
    
    def hide_spinner(self):
        self.pack_forget()
        self.spinner_running = False
        self.root.update()        

    def run_with_spinner(self, func: Callable):
        self.show_spinner()
        threading.Thread(target=lambda: func()).start()
