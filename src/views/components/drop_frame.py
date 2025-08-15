import tkinter as tk
import os
from typing import Callable

from models.main_model import MainModel

DND_BG_COLOR = "#f0f0f0"

class DropFrame(tk.Frame):
    def __init__(self, root, model: MainModel, upload_handler: Callable, drop_handler: Callable, ui_reset_handler: Callable, delete_file_handler: Callable):
        self.max_visible_rows = 5

        self.model = model
        self.upload_handler = upload_handler
        self.drop_handler = drop_handler
        self.dnd_bg_color = DND_BG_COLOR
        self.ui_reset_handler = ui_reset_handler
        self.delete_file_handler = delete_file_handler

        super().__init__(
            root,
            width=650,
            height=200,
            bg=self.dnd_bg_color,
            highlightbackground="gray",
            highlightthickness=2
        )

        self.configure_dnd(self)

        self.drop_target_register('DND_Files')
        self.dnd_bind('<<Drop>>', self.drop_handler)

        self.scroll_canvas = tk.Canvas(self, bg=self.dnd_bg_color, highlightthickness=0)
        self.scroll_frame = tk.Frame(self.scroll_canvas, bg=self.dnd_bg_color)
        self.scrollbar = tk.Scrollbar(
            self, 
            orient="vertical",
            command=self.scroll_canvas.yview
        )

        self.scroll_canvas.config(yscrollcommand=self.scrollbar.set)

        self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )

        self.bind(
            "<MouseWheel>",
            lambda event: self.scroll_canvas.yview_scroll(int(-1 * (event.delta/120)), "units") 
        )

        self.configure_dnd(self.scroll_canvas)
        self.configure_dnd(self.scroll_frame)

        self.upload_btn = tk.Button(
            self, 
            text="Click to Select File(s)\nor Drag and Drop", 
            font=("Segoe UI", 14), 
            command=self.upload_handler, 
            bg="#007BFF", 
            fg="white", 
            width=20, 
            height=2
        )
        self.upload_btn.place(relx=0.5, rely=0.5, anchor="center")

        self.clear_files_btn = tk.Button( 
            root,
            text="Clear",
            font=("Segoe UI", 14),
            command=lambda: [self.model.clean_uploads(), self.ui_reset_handler()],
            bg="#545151",
            fg="white",
            width=10,
            height=1
        )

    def configure_dnd(self, widget: tk.Widget):
        widget.drop_target_register('DND_Files')
        widget.dnd_bind('<<Drop>>', self.drop_handler)

        # Allow clicking to open file dialog
        widget.bind("<Button-1>", lambda e: self.upload_handler())

        widget.dnd_bind('<<DragEnter>>', lambda e: widget.config(bg="#d0f0d0"))
        widget.dnd_bind('<<DragLeave>>', lambda e: widget.config(bg=self.dnd_bg_color))

    def show_file_list_frame(self):
        self.upload_btn.place_forget()
        row_height = 30
        visible_rows = min(len(self.model.uploaded_files)+1, self.max_visible_rows)
        actual_height = row_height * visible_rows
        max_height = row_height * self.max_visible_rows
        relheight = actual_height / max_height - 0.02

        self.scroll_canvas.place(relx=0.02, rely=0.02, relwidth=0.9, relheight=relheight)
        self.scroll_frame.config(height=relheight)
        
        if len(self.model.uploaded_files)-1 > self.max_visible_rows:
            self.scrollbar.place(relx=0.92, rely=0.02, relheight=relheight)
        else:
            self.scrollbar.place_forget()
        
        self.clear_files_btn.pack(side="bottom", pady=10)

    def hide_file_list_frame(self):     
        self.upload_btn.place(relx=0.5, rely=0.5, anchor="center")
        self.clear_files_btn.pack_forget()
        self.scroll_canvas.place_forget()
        self.scrollbar.place_forget()

    def update_file_display(self): 
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not self.model.uploaded_files:
            self.hide_file_list_frame()
            return
        self.show_file_list_frame()

        for file in self.model.uploaded_files:
            row = tk.Frame(self.scroll_frame, bg=self.dnd_bg_color)
            row.pack(fill="x", padx=4, pady=2)

            label = tk.Button(row, text=self.model.limit_file_name(os.path.basename(file)), bg=self.dnd_bg_color, anchor="w")
            label.pack(side="left", fill="x", expand=True)

            btn = tk.Button(row, 
                text="❌", 
                command=lambda f=file: self.delete_file_handler(f),
                bg=self.dnd_bg_color,
                fg="black",
                padx=6
            )

            if self.model.selected_application_file and file == self.model.selected_application_file:
                label.config(bg='#bfbfbf')

            btn.pack(side="right", padx=5)
        
        self.make_scrollable_for_file_list(self)        

    def make_scrollable_for_file_list(self, widget: tk.Widget): 
        if not widget:
            return
        if not self.scrollbar.winfo_ismapped():
            widget.unbind("<MouseWheel>")
        else:
            widget.bind(
                "<MouseWheel>",
                lambda event: self.scroll_canvas.yview_scroll(int(-1 * (event.delta/120)), "units") 
            )
        for w in widget.winfo_children():
            self.make_scrollable_for_file_list(w)