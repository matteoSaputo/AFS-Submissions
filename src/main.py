from tkinterdnd2 import TkinterDnD as tk
from controllers.app import App

# --- Start app ---
def main():
    root = tk.Tk()    
    app = App(root)
    root.mainloop()
    app.main_frame.submissions_controller.model.clean_uploads_folder()

if __name__ == "__main__":
    main()