"""
submissions_model: Data model for handling AFS submissions.

Extends MainModel to provide business logic for processing, preparing, and managing AFS application submissions, including file extraction, PDF flattening, and folder matching.
"""

import os

# Import super class
from models.main_model import MainModel

# Import relevant business logic modules
from models.utils.process_submission import process_submission as _process_submission, prepare_submission as _prepare_submission
from models.utils.afs_parser import is_likely_application as _is_likely_application
from models.utils.extract_zip import extract_zip as _extract_zip
from models.utils.flatten_pdf import flatten_pdf as _flatten_pdf, flatten_pdf_preserving_fields as _flatten_pdf_preserving_fields

class SubmissionsModel(MainModel):
    """Model for AFS submissions.

    Attributes
    ----------
    selected_application_file : str or None
        Path to the selected application file.
    application_file_type : str or None
        Type of the application file.
    afs_data : dict or None
        Extracted AFS application data.
    missing_vlaues : dict or None
        Dictionary of missing values in the application.
    bus_name : str or None
        Business name for the submission.
    customer_folder : str or None
        Customer folder path.
    matched_folder : str or None
        Matched folder name.
    match_score : int or None
        Score for folder matching.
    full_package : bool
        Whether the submission is a full package.
    full_packages_folder : str or None
        Path to the full packages folder.
    """

    def __init__(self):
        """Initialize the SubmissionsModel and set up submission attributes."""
        super().__init__()
        self.version = self.get_version()
    
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
        """Process the current submission using business logic modules."""
        return _process_submission(
            self.selected_application_file,
            self.uploaded_files,
            self.afs_data,
            self.missing_vlaues,
            self.application_file_type,
            self.bus_name,
            self.customer_folder
        )
    
    def prepare_submission(self, document_purpose="Application"):
        """Prepare submission data and update model attributes.

        Parameters
        ----------
        document_purpose : str, optional
            Purpose of the document (default: "Application").

        Returns
        -------
        tuple
            Submission data, missing values, selected file, business name, matched folder, match score, full package.
        """
        self.afs_data, self.missing_vlaues, self.application_file_type, self.bus_name, self.matched_folder, self.match_score, self.full_package = _prepare_submission(self.selected_application_file, self.drive, document_purpose)
        return self.afs_data, self.missing_vlaues, self.selected_application_file, self.bus_name, self.matched_folder, self.match_score, self.full_package
    
    def is_likely_application(self, file_path):
        """Check if the given file is likely an AFS application.

        Parameters
        ----------
        file_path : str
            Path to the file to check.

        Returns
        -------
        bool
            True if the file is likely an application, else False.
        """
        return _is_likely_application(file_path)
    
    def extract_zip(self, zip_path):
        """Extract files from a ZIP archive.

        Parameters
        ----------
        zip_path : str
            Path to the ZIP archive.

        Returns
        -------
        list
            List of extracted file paths.
        """
        return _extract_zip(zip_path)

    def flatten_pdf(self, path):
        """Flatten a PDF file in place.

        Parameters
        ----------
        path : str
            Path to the PDF file to flatten.

        Returns
        -------
        str
            Path to the flattened PDF file.
        """
        return _flatten_pdf(path, path)
    
    def flatten_pdf_preserving_fields(self, path):
        """Flatten a PDF file while preserving form fields.

        Parameters
        ----------
        path : str
            Path to the PDF file to flatten.

        Returns
        -------
        str
            Path to the flattened PDF file.
        """
        return _flatten_pdf_preserving_fields(path, path)
