"""
resource_path: Utility for locating resource files.

Provides a function to get the absolute path to a resource, compatible with both development and PyInstaller environments.
"""

import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller.

    Parameters
    ----------
    relative_path : str
        Relative path to the resource file.

    Returns
    -------
    str
        Absolute path to the resource file.
    """
    try:
        base_path = sys._MEIPASS  # created by PyInstaller at runtime
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.abspath(os.path.join(base_path, relative_path))
