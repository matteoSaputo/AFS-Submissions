import os
import sys

def get_user_data_path(filename):
    """Return a writable location for config data"""
    if getattr(sys, 'frozen', False):
        # If bundled
        base = os.path.expanduser("~\\AppData\\Local\\AFS_Submission_Tool")
    else:
        # During normal dev
        base = os.path.abspath(".")

    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)


