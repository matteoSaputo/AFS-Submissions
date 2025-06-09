from tkinterdnd2 import TkinterDnD as tk
from controllers.main.main_controller import MainController

# --- Start app ---
def main():
    root = tk.Tk()    
    app = MainController(root)
    root.mainloop()
    app.submissions_controller.model.clean_uploads_folder()

if __name__ == "__main__":
    main()