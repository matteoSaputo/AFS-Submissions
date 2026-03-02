"""
user_data: Utility for locating user-specific config and data files.

Provides a function to get a writable path for storing user data, handling both development and bundled (PyInstaller) environments.
"""

import os
import sys

def get_user_data_path(filename):
    """Return a writable location for config data.

    Parameters
    ----------
    filename : str
        Name of the config/data file.

    Returns
    -------
    str
        Absolute path to the writable file location.
    """
    if getattr(sys, 'frozen', False):
        # If bundled
        base = os.path.expanduser("~\\AppData\\Local\\AFS_Submission_Tool\\info")
    else:
        # During normal dev
        base = os.path.abspath("./info")

    os.makedirs(base, exist_ok=True)
    return os.path.join(base, filename)


