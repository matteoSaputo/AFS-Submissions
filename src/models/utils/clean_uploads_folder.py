import os
import shutil

def clean_uploads(upload_dir):
    files_to_delete =[
        f for f in os.listdir(upload_dir) if f != "keep.txt"
    ]

    if not files_to_delete:
        return
    
    for file in files_to_delete:
        file_path = os.path.join(upload_dir, file)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. {e}")