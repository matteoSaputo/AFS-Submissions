from tkinterdnd2 import TkinterDnD
from gui.gui_utils.file_handling import clean_uploads_folder
from gui.app import AFSApp

# --- Start app ---
if __name__ == "__main__":
    root = TkinterDnD.Tk()    
    app = AFSApp(root)
    root.mainloop()
    clean_uploads_folder(app)