from tkinterdnd2 import TkinterDnD as tk
from controllers.main_controller import MainController
from models.utils.lo_manager import ensure_lo_started

# --- Start app ---
def main():
    root = tk.Tk()    
    app = MainController(root)
    ensure_lo_started()
    root.mainloop()
    app.submissions_controller.model.clean_uploads()

if __name__ == "__main__":
    main()