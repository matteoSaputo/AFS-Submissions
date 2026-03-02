"""
contracts_service: Service layer for handling file operations in contracts.

Handles extraction, copying, and identification of likely agreement or application files for contract submissions.
"""

import os
import shutil
from models.services.submissions_service import SubmissionService
from models.contracts_model import ContractsModel

class ContracstService(SubmissionService):
    """Service for file operations in contracts.

    Parameters
    ----------
    model : ContractsModel
        The contracts model instance.
    """

    def __init__(self, model: ContractsModel):
        """Initialize the ContracstService with the given contracts model.

        Parameters
        ----------
        model : ContractsModel
            The contracts model instance.
        """
        super().__init__(model)
        self.model = model

    def handle_files(self, file_list):
        """Handle file extraction, copying, and agreement/application detection.

        Parameters
        ----------
        file_list : list
            List of file paths to process.
        Returns
        -------
        str
            Path to the likely agreement or application file, if found.
        """
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
            is_agreement = self.model.is_likely_agreement(temp_file)
            is_application = self.model.is_likely_application(temp_file)
            likely_agreement_found = is_agreement or is_application
            if likely_agreement_found:
                likely_agreement = file
                if is_application:
                    self.model.document_type = 'Application'
                if is_agreement:
                    self.model.document_type = 'Contract'
            os.remove(temp_file)
                
        if likely_agreement:
            self.model.selected_application_file = likely_agreement
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
    
    def reset_model_state(self):
        """Reset contract-specific model state and call parent reset."""
        self.model.bus_name = ""
        self.model.phone = ""
        self.model.fee_percent = None
        self.model.ein = ""
        self.model.frequency = ""
        self.model.interest_rate = None
        self.model.routing_number = ""
        self.model.account_number = ""
        self.model.bank_name = ""
        self.model.loc_amount = None
        self.model.funding_amout = None
        self.model.owner_name = ""
        self.model.date = ""
        return super().reset_model_state()