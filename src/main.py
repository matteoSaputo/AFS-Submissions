from tkinterdnd2 import TkinterDnD
from app import AFSApp

# --- Start app ---
if __name__ == "__main__":
    root = TkinterDnD.Tk()    
    app = AFSApp(root)
    root.mainloop()
    app.clean_uploads_folder()