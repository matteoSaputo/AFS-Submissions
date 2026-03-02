"""
get_version: Utility for retrieving the application version string.

Reads the version from 'info/version.txt' or returns 'vUnknown' if not found.
"""

import os
from models.utils.resource_path import resource_path

def get_version():
    """Get the application version string from file.

    Returns
    -------
    str
        Application version string.
    """
    version_file = resource_path("info/version.txt")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "vUnknown"