import tkinter as tk

from gui.gui_utils.file_handling import handle_drop, upload_pdf

def allow_dropping_and_clicking(app, widget):
    widget.drop_target_register('DND_Files')
    widget.dnd_bind('<<Drop>>', lambda event: handle_drop(app, event))

    # Allow clicking to open file dialog
    widget.bind("<Button-1>", lambda: upload_pdf(app))

    widget.dnd_bind('<<DragEnter>>', lambda e: widget.config(bg="#d0f0d0"))
    widget.dnd_bind('<<DragLeave>>', lambda e: widget.config(bg=app.dnd_bg_color))

def create_drop_frame(app):
    drop_frame = tk.Frame(
        app.root,
        width=650,
        height=200,
        bg=app.dnd_bg_color,
        highlightbackground="gray",
        highlightthickness=2
    )
    drop_frame.pack(pady=10)

    allow_dropping_and_clicking(app, drop_frame)

    scroll_canvas = tk.Canvas(drop_frame, bg=app.dnd_bg_color, highlightthickness=0)
    scroll_frame = tk.Frame(scroll_canvas, bg=app.dnd_bg_color)
    scrollbar = tk.Scrollbar(
        drop_frame, 
        orient="vertical",
        command=scroll_canvas.yview
    )

    scroll_canvas.config(yscrollcommand=scrollbar.set)

    scroll_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    scroll_frame.bind(
        "<Configure>",
        lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
    )

    drop_frame.bind(
        "<MouseWheel>",
        lambda event: scroll_canvas.yview_scroll(int(-1 * (event.delta/120)), "units") 
    )

    allow_dropping_and_clicking(app, scroll_canvas)
    allow_dropping_and_clicking(app, scroll_frame)

    return drop_frame, scroll_canvas, scroll_frame, scrollbar

def create_upload_btn(app):
    upload_btn = tk.Button(
        app.drop_frame, 
        text="Click to Select File(s)\nor Drag and Drop", 
        font=("Segoe UI", 14), 
        command=lambda: upload_pdf(app), 
        bg="#007BFF", 
        fg="white", 
        width=20, 
        height=2
    )
    upload_btn.place(relx=0.5, rely=0.5, anchor="center")
    return upload_btn