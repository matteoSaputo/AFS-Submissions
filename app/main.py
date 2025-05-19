from tkinterdnd2 import TkinterDnD
from gui.afs_app import AFSApp

# --- Start app ---
if __name__ == "__main__":
    root = TkinterDnD.Tk()    
    app = AFSApp(root)
    root.mainloop()
    app.clean_uploads_folder()