import os
from models.submissions_model import SubmissionsModel

AGREEMENTS_FOLDER = "data/templates/agreements"

class ContractsModel(SubmissionsModel):
    def __init__(self):
        super().__init__()
        self.agreements = os.listdir(self.resource_path(AGREEMENTS_FOLDER))

        self.fee_percent = None
        self.frequency = ""
        self.interest_rate = None
        self.routing_number = None
        self.account_number = None
        self.bank_name = None
        self.loc_amount = None
        self.funding_amout = None
