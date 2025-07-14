from models.utils.get_version import get_version as _get_version
from models.utils.user_data import get_user_data_path as _get_user_data_path
from models.utils.resource_path import resource_path as _resource_path

class MainModel:
    def __init__(self):
        self.version = self.get_version()

    def get_version(self):
        return _get_version()
    
    def get_user_data_path(self, filename):
        return _get_user_data_path(filename)
    
    def resource_path(self, relative_path):
        return _resource_path(relative_path)