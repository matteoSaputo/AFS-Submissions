import os 
import shutil 
import pandas as pd

from models.submissions_model import SubmissionsModel

class SubmissionService:
    def __init__(self, model: SubmissionsModel):
        self.model = model

    def handle_files(self, file_list):
        extracted_files = []

        for original_path in file_list:
            if original_path.lower().endswith(".zip"):
                file_list.extend(self.model.extract_zip(original_path))
                continue
            extracted_files.append(original_path)

        likely_application = ""
        for file in extracted_files:
            if self.model.is_likely_application(file):
                likely_application = file
                
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
        self.model.prepare_submission()

    def finalize_submission(self, use_existing):
        if self.model.matched_folder and use_existing:
            self.model.customer_folder = os.path.join(self.model.drive, self.model.matched_folder)
        else:
            self.model.customer_folder = os.path.join(self.model.drive, self.model.bus_name)

        self.model.process_submission()

    def prepare_full_packages(self):
        fp_folder_path = os.path.join(self.model.drive, "csv_apps")
        os.makedirs(fp_folder_path, exist_ok=True)
        self.model.full_packages_folder = fp_folder_path

        for field, value in self.model.afs_data.items():
            path = os.path.join(self.model.full_packages_folder, f"{field}.csv")
            pd.DataFrame([value[0]]).to_csv(path, index=False)

    def reset_model_state(self):
        self.model.uploaded_files = []
        self.model.selected_application_file = None
        self.model.customer_folder = None
        self.model.matched_folder = None
        self.model.match_score = 0
        self.model.bus_name = ""
        self.model.full_package = False
        self.model.clean_uploads()

    def delete_file(self, file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
        if file_path in self.model.uploaded_files:
            self.model.uploaded_files.remove(file_path)
        if file_path == self.model.selected_application_file:
            self.model.selected_application_file = None
            self.reset_model_state()

    def limit_file_name(self, file, limit=50):
        name, extension = os.path.splitext(file)
        return f"{name[:limit]}...{extension}" if len(file) > limit else file