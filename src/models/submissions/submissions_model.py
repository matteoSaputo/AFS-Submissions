import os

# Import super class
from models.main.main_model import MainModel

# Import relevant business logic modules
from models.utils.process_submission import process_submission as _process_submission, prepare_submission as _prepare_submission
from models.utils.afs_parser import is_likely_application as _is_likely_application
from models.utils.extract_zip import extract_zip as _extract_zip
from models.utils.clean_uploads_folder import clean_uploads as _clean_uploads

class SubmissionsModel(MainModel):
    def __init__(self, upload_dir):
        super().__init__()

        self.upload_dir = self.resource_path(upload_dir)
        self.version = self.get_version()
        self.drive = None
        self.uploaded_files = []
        self.selected_application_file = None
        self.application_file_type = None
        self.afs_data = None
        self.missing_vlaues = None
        self.bus_name = None
        self.customer_folder = None
        self.matched_folder = None
        self.match_score = None
        self.full_package = False
        self.full_packages_folder = None

        # Create upload dir if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)

    def process_submission(self):
        return _process_submission(
            self.selected_application_file,
            self.uploaded_files,
            self.afs_data,
            self.missing_vlaues,
            self.application_file_type,
            self.bus_name,
            self.customer_folder
        )
    
    def prepare_submission(self):
        self.afs_data, self.missing_vlaues, self.application_file_type, self.bus_name, self.matched_folder, self.match_score, self.full_package = _prepare_submission(self.selected_application_file, self.drive)
        return self.afs_data, self.missing_vlaues, self.selected_application_file, self.bus_name, self.matched_folder, self.match_score, self.full_package
    
    def is_likely_application(self, file_path):
        return _is_likely_application(file_path)
    
    def extract_zip(self, zip_path):
        return _extract_zip(zip_path)
    
    def clean_uploads(self):
        return _clean_uploads(self.upload_dir)

