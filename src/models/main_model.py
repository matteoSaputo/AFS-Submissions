"""
MainModel: Core data model for AFS Submissions Tool.

Handles versioning, drive path management, resource location, and uploads folder cleanup. Provides helper methods for accessing user data and resources.
"""

import os

from models.utils.get_version import get_version as _get_version
from models.utils.user_data import get_user_data_path as _get_user_data_path
from models.utils.resource_path import resource_path as _resource_path
from models.utils.clean_uploads_folder import clean_uploads as _clean_uploads

# --- Global constants ---
UPLOAD_DIR = "data/uploads"

class MainModel:
    """Main application data model.

    Attributes
    ----------
    version : str
        Application version string.
    drive : str or None
        Path to the current drive folder.
    upload_dir : str
        Path to the uploads directory.
    uploaded_files : list
        List of uploaded files.
    """

    def __init__(self):
        """Initialize the MainModel and set up version, drive, and uploads directory."""
        self.version = self.get_version()
        self.drive = self.load_drive_path()
        self.upload_dir = self.resource_path(UPLOAD_DIR)
        self.uploaded_files = []

    def get_version(self):
        """Get the application version string."""
        return _get_version()
    
    def get_user_data_path(self, filename):
        """Get the path for user-specific config/data files.

        Parameters
        ----------
        filename : str
            Name of the config/data file.
        Returns
        -------
        str
            Absolute path to the writable file location.
        """
        return _get_user_data_path(filename)
    
    def resource_path(self, relative_path):
        """Get the absolute path to a resource file.

        Parameters
        ----------
        relative_path : str
            Relative path to the resource file.
        Returns
        -------
        str
            Absolute path to the resource file.
        """
        return _resource_path(relative_path)
    
    def clean_uploads(self):
        """Delete all files and folders in the uploads directory except 'keep.txt'."""
        return _clean_uploads(self.upload_dir)
    
    def load_drive_path(self):
        """Load the drive path from user data, if it exists."""
        drive_path_file = self.get_user_data_path("drive_path.txt")   

        if os.path.exists(drive_path_file):
            with open(drive_path_file, "r") as f:
                drive_path = f.read().strip()
                if os.path.exists(drive_path):
                    return drive_path
        return None
    
    def change_drive_path(self, drive_path):
        """Change and save the drive path to user data.

        Parameters
        ----------
        drive_path : str
            New drive path to set.
        Returns
        -------
        str or None
            The new drive path if set, else None.
        """
        drive_path_file = self.get_user_data_path("drive_path.txt")   

        if drive_path:
            with open(drive_path_file, "w") as f:
                f.write(drive_path)
            self.drive = drive_path
            return drive_path
        
    def limit_file_name(self, file, limit=50):
        """Limit the length of a file name for display purposes.

        Parameters
        ----------
        file : str
            The file name to limit.
        limit : int, optional
            Maximum length before truncation (default: 50).
        Returns
        -------
        str
            Truncated file name with ellipsis if needed.
        """
        name, extension = os.path.splitext(file)
        return f"{name[:limit]}...{extension}" if len(file) > limit else file