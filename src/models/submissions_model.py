import os

# Import relevant business logic modules
from models.utils.process_submission import process_submission as process_submission_util, prepare_submission as prepare_submission_util
from models.utils.afs_parser import is_likely_application as is_likely_application_util
from models.utils.user_data import get_user_data_path as get_user_data_path_util
from models.utils.get_version import get_version as get_version_util
from models.utils.resource_path import resource_path as resource_path_util
from models.utils.extract_zip import extract_zip as extract_zip_util
from models.utils.clean_uploads_folder import clean_uploads_folder as clean_uploads_folder_util

class SubmissionsModel:
    def __init__(self, upload_dir):
        self.upload_dir = self.resource_path(upload_dir)
        
        # Create upload dir if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)


    def process_submission(self, upload_path, attatchements, afs_data, bus_name, customer_folder):
        return process_submission_util(
            upload_path,
            attatchements,
            afs_data,
            bus_name,
            customer_folder
        )
    
    def prepare_submission(self, afs_path, drive):
        return prepare_submission_util(afs_path, drive)
    
    def is_likely_application(self, file_path):
        return is_likely_application_util(file_path)
    
    def get_user_data_path(self, filename):
        return get_user_data_path_util(filename)

    def get_version(self):
        return get_version_util()
    
    def resource_path(self, relative_path):
        return resource_path_util(relative_path)
    
    def extract_zip(self, zip_path):
        return extract_zip_util(zip_path)
    
    def clean_uploads_folder(self):
        return clean_uploads_folder_util(self.upload_dir)

