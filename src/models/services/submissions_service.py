"""
submissions_service: Service layer for handling file operations in submissions.

Handles extraction, copying, and identification of likely application files for AFS submissions.
"""

import os 
import shutil 
import pandas as pd

from models.submissions_model import SubmissionsModel

class SubmissionService:
    """Service for file operations in submissions.

    Parameters
    ----------
    model : SubmissionsModel
        The submissions model instance.
    """

    def __init__(self, model: SubmissionsModel):
        """Initialize the SubmissionService with the given submissions model.

        Parameters
        ----------
        model : SubmissionsModel
            The submissions model instance.
        """
        self.model = model

    def handle_files(self, file_list):
        """Handle file extraction, copying, and application detection.

        Parameters
        ----------
        file_list : list
            List of file paths to process.
        Returns
        -------
        str
            Path to the likely application file, if found.
        """

        extracted_files = []

        for original_path in file_list:
            if original_path.lower().endswith(".zip"):
                file_list.extend(self.model.extract_zip(original_path))
                continue
            extracted_files.append(original_path)

        likely_application = ""
        for file in extracted_files:
            ext = os.path.splitext(file)[1]
            temp_file = self.model.resource_path(f"temp_upload.{ext}")
            shutil.copy(file, temp_file)
            # self.model.flatten_pdf(temp_file)
            likely_application_found = self.model.is_likely_application(temp_file)
            if likely_application_found:
                likely_application = file
            os.remove(temp_file)
                
        if likely_application:
            self.model.clean_uploads()

        for file in extracted_files:
            filename = os.path.basename(file)
            dest_path = os.path.join(self.model.upload_dir, filename)
            if not os.path.exists(dest_path):
                shutil.copy(file, dest_path)
            if filename == os.path.basename(likely_application):
                self.model.selected_application_file = dest_path
            self.model.uploaded_files.append(dest_path)

        return likely_application

    def prepare_submission(self):
        """Prepare the submission by updating the model's state."""
        self.model.prepare_submission()

    def finalize_submission(self, use_existing):
        """Finalize the submission, setting the customer folder and processing the submission.

        Parameters
        ----------
        use_existing : bool
            Whether to use the matched folder or create a new one.
        """
        if self.model.matched_folder and use_existing:
            self.model.customer_folder = os.path.join(self.model.drive, self.model.matched_folder)
        else:
            self.model.customer_folder = os.path.join(self.model.drive, self.model.bus_name)

        self.model.process_submission()

    def prepare_full_packages(self):
        """Prepare full package CSV files for all AFS data fields."""
        fp_folder_path = os.path.join(self.model.drive, "csv_apps")
        os.makedirs(fp_folder_path, exist_ok=True)
        self.model.full_packages_folder = fp_folder_path

        for field, value in self.model.afs_data.items():
            path = os.path.join(self.model.full_packages_folder, f"{field}.csv")
            try:
                pd.DataFrame([value[0]]).to_csv(path, index=False)
            except Exception as e:
                pd.DataFrame([value]).to_csv(path, index=False)
                # print(f"Error writing full package for field {field} and value {value}: {e}")

    def reset_model_state(self):
        """Reset the model's state for a new submission."""
        self.model.uploaded_files = []
        self.model.selected_application_file = None
        self.model.customer_folder = None
        self.model.matched_folder = None
        self.model.match_score = 0
        self.model.bus_name = ""
        self.model.full_package = False
        self.model.clean_uploads()

    def delete_file(self, file_path):
        """Delete a file from the file system and update the model's state.

        Parameters
        ----------
        file_path : str
            The path of the file to delete.
        """
        if os.path.exists(file_path):
            os.remove(file_path)
        if file_path in self.model.uploaded_files:
            self.model.uploaded_files.remove(file_path)
        if file_path == self.model.selected_application_file:
            self.model.selected_application_file = None
            self.reset_model_state()

    def limit_file_name(self, file, limit=50):
        """Limit the file name length to the specified limit.

        Parameters
        ----------
        file : str
            The original file name.
        limit : int
            The maximum length of the file name.

        Returns
        -------
        str
            The modified file name, truncated and appended with '...' if it exceeds the limit.
        """
        name, extension = os.path.splitext(file)
        return f"{name[:limit]}...{extension}" if len(file) > limit else file