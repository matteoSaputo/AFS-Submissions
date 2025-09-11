import os
import shutil
from controllers.submissions_service import SubmissionService
from models.contracts_model import ContractsModel

class ContracstService(SubmissionService):
    def __init__(self, model: ContractsModel):
        super().__init__(model)
        self.model = model

    def handle_files(self, file_list):
        extracted_files = []

        for original_path in file_list:
            if original_path.lower().endswith(".zip"):
                file_list.extend(self.model.extract_zip(original_path))
                continue
            extracted_files.append(original_path)

        likely_agreement = ""
        for file in extracted_files:
            temp_file = self.model.resource_path("temp_upload.pdf")
            shutil.copy(file, temp_file)
            likely_agreement_found = self.model.is_likely_agreement(temp_file) or self.model.is_likely_application(temp_file)
            if likely_agreement_found:
                likely_agreement = file
            os.remove(temp_file)
                
        if likely_agreement:
            self.model.clean_uploads()

        for file in extracted_files:
            filename = os.path.basename(file)
            dest_path = os.path.join(self.model.upload_dir, filename)
            if not os.path.exists(dest_path):
                shutil.copy(file, dest_path)
            if filename == os.path.basename(likely_agreement):
                self.model.selected_application_file = dest_path
            self.model.uploaded_files.append(dest_path)

        return likely_agreement