import os

from models.utils.get_version import get_version as _get_version
from models.utils.user_data import get_user_data_path as _get_user_data_path
from models.utils.resource_path import resource_path as _resource_path

class MainModel:
    def __init__(self):
        self.version = self.get_version()
        self.drive = self.load_drive_path()

    def get_version(self):
        return _get_version()
    
    def get_user_data_path(self, filename):
        return _get_user_data_path(filename)
    
    def resource_path(self, relative_path):
        return _resource_path(relative_path)
    
    def load_drive_path(self):
        drive_path_file = self.get_user_data_path("drive_path.txt")   

        if os.path.exists(drive_path_file):
            with open(drive_path_file, "r") as f:
                drive_path = f.read().strip()
                if os.path.exists(drive_path):
                    return drive_path
        return None
    
    def change_drive_path(self, drive_path):
        drive_path_file = self.get_user_data_path("drive_path.txt")   

        if drive_path:
            with open(drive_path_file, "w") as f:
                f.write(drive_path)
            self.drive = drive_path
            return drive_path