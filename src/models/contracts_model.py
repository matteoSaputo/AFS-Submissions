import os
from models.submissions_model import SubmissionsModel
from models.utils.afs_parser import is_likely_agreement as _is_likely_agreement

AGREEMENTS_FOLDER = "data/templates/agreements"

class ContractsModel(SubmissionsModel):
    def __init__(self):
        super().__init__()
        self.agreements = os.listdir(self.resource_path(AGREEMENTS_FOLDER))

        self.fee_percent = None
        self.frequency = ""
        self.interest_rate = None
        self.routing_number = ""
        self.account_number = ""
        self.bank_name = ""
        self.loc_amount = None
        self.funding_amout = None

    def is_likely_agreement(self, file_path):
        return _is_likely_agreement(file_path)
    
    def prepare_submission(self):
        return super().prepare_submission(document_purpose="Contract")
    