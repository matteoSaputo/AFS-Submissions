from tkinterdnd2 import TkinterDnD
from controllers.app import AFSApp

# --- Start app ---
def main():
    root = TkinterDnD.Tk()    
    app = AFSApp(root)
    root.mainloop()
    app.clean_uploads_folder()

if __name__ == "__main__":
    main()