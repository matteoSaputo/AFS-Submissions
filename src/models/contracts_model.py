import os
from models.submissions_model import SubmissionsModel
from models.utils.afs_parser import is_likely_agreement as _is_likely_agreement
from models.utils.process_submission import process_contracts as _process_contracts

AGREEMENTS_FOLDER = "data/templates/agreements"

class ContractsModel(SubmissionsModel):
    def __init__(self):
        super().__init__()
        self.agreements = os.listdir(self.resource_path(AGREEMENTS_FOLDER))

        self.business_name = ""
        self.phone = ""
        self.fee_percent = None
        self.ein = ""
        self.frequency = ""
        self.interest_rate = None
        self.routing_number = ""
        self.account_number = ""
        self.bank_name = ""
        self.loc_amount = None
        self.funding_amout = None
        self.owner_name = ""
        self.date = ""

    def is_likely_agreement(self, file_path):
        return _is_likely_agreement(file_path)
    
    def prepare_submission(self):
        super().prepare_submission(document_purpose="Contract")
        self.business_name = self.afs_data["Merchant Name"]
        self.phone = self.afs_data["Phone"]
        self.ein = self.afs_data["EIN"]
        self.routing_number = self.afs_data["Routing Number"]
        self.account_number = self.afs_data["Account Number"]
        self.bank_name = self.afs_data["Bank"]
        self.loc_amount = self.afs_data["LOC Amount"]
        self.funding_amout = self.afs_data["Initial Funding"]
        self.owner_name = self.afs_data["Primary Owner Name"]
        self.date = self.afs_data["Date"]  

    def process_submission(self):
        return _process_contracts(
            self.selected_application_file,
            self.uploaded_files,
            self.afs_data,
            self.bus_name,
            self.customer_folder
        )