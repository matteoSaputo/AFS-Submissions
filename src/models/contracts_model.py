"""
contracts_model: Data model for handling contract submissions and agreements.

Extends SubmissionsModel to provide business logic for contract-specific data extraction, formatting, and processing, including agreement detection, field normalization, and formatting utilities for money, percent, phone, EIN, and state abbreviations.
"""

import os
import re
from models.submissions_model import SubmissionsModel
from models.utils.afs_parser import is_likely_agreement as _is_likely_agreement
from models.utils.process_submission import process_contracts as _process_contracts

AGREEMENTS_FOLDER = "data/templates/agreements"
ACRONYMS = [
    "DBA", "LLC"  
]
INTEREST_RATE_MAPPING = {
    "1.0": "one",
    "1.25": "one and a quarter",
    "1.5": "one and a half"
}
US_STATE_ABBREVIATION = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}


class ContractsModel(SubmissionsModel):
    """Model for contract submissions and agreements.

    Attributes
    ----------
    agreements : list
        List of available agreement templates.
    phone : str
        Phone number for the contract.
    fee_percent : float or None
        Fee percentage for the contract.
    ein : str
        EIN for the contract.
    frequency : str
        Payment frequency.
    interest_rate : float or None
        Interest rate for the contract.
    routing_number : str
        Bank routing number.
    account_number : str
        Bank account number.
    bank_name : str
        Name of the bank.
    loc_amount : float or None
        Line of credit amount.
    funding_amout : float or None
        Initial funding amount.
    owner_name : str
        Owner name.
    co_owner_name : str or None
        Co-owner name.
    date : str
        Date of the contract.
    document_type : str
        Type of document (e.g., contract, application).
    """

    def __init__(self):
        super().__init__()
        self.agreements = os.listdir(self.resource_path(AGREEMENTS_FOLDER))

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
        self.co_owner_name = ""
        self.date = ""
        self.document_type = ""
        self.heloc_amount = ""
        self.heloc_rate = ""

    def is_likely_agreement(self, file_path):
        """Check if the given file is likely a contract agreement."""
        return _is_likely_agreement(file_path)
    
    def prepare_submission(self):
        """Prepare contract submission data and assign variables."""
        super().prepare_submission(document_purpose="Contract")
        self._assign_vars()

    def process_submission(self):
        """Process the current contract submission using business logic modules."""
        self.afs_data["Interest Rate"] = INTEREST_RATE_MAPPING[self.afs_data["Interest Rate"]]
        self.afs_data["Frequency"] = self.afs_data["Frequency"].lower()
        self.bus_name = self.afs_data["Merchant Name"]
        return _process_contracts(
            self.selected_application_file,
            self.uploaded_files,
            self.afs_data,
            self.bus_name,
            self.customer_folder
        )
    
    def _assign_vars(self):
        """Assign extracted AFS data to contract model attributes."""
        self.phone = self.afs_data["Tele No"]
        self.ein = self.afs_data["EIN"]
        self.routing_number = self.afs_data["Routing"]
        self.account_number = self.afs_data["Account"]
        self.bank_name = self.afs_data["Bank"]
        self.loc_amount = self.afs_data["Line of Credit"]
        self.funding_amout = self.afs_data["Initial Funding"]
        self.owner_name = self.afs_data["Owner Name"]
        self.co_owner_name = self.afs_data.get("Co-Owner Name")
        self.date = self.afs_data["Date"]
        self.heloc_amount = self.afs_data.get("HELOC Amount")
        self.heloc_amount = self.afs_data.get("HELOC Rate")
    
    def _money_to_float(self, s: str | None) -> float | None:
        """Convert a money string to a float value."""
        if not s:
            return None
        # drop anything that isn't digit or dot/comma, then normalize commas
        cleaned = re.sub(r"[^0-9.,-]", "", s)
        # if both comma and dot appear, assume comma = thousands
        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(",", "")
        else:
            # if only comma appears, treat it as decimal
            cleaned = cleaned.replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
        
    def _percent_to_float(self, s: str) -> float | None:
        """Convert a percent string to a float value."""
        if s is None:
            return None
        s = s.strip()
        if not s:
            return None
        s = s.replace('%', '').strip()
        try:
            return float(s) if s else None
        except ValueError:
            return None
    
    def _fmt_money(self, x: float | None) -> str:
        """Format a float as a money string."""
        if x is None:
            return ""
        return f"{x:,.2f}"

    def _fmt_percent(self, x: float | None) -> str:
        """Format a float as a percent string."""
        if x is None:
            return ""
        return f"{x:.1f}%"
    
    def _fmt_phone(self, x: str | None) -> str:
        """Format a phone number string."""
        if x is None:
            return ""
        digits = re.sub(r"\D", "", x)

        formatted = ""
        if len(digits) >= 1:
            formatted = "(" + digits[:3]
        if len(digits) >= 4:
            formatted = f"({digits[:3]}) {digits[3:6]}"
        if len(digits) >= 7:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:10]}"

        # handle partial input gracefully
        if len(digits) < 3:
            formatted = "(" + digits
        elif 3 <= len(digits) < 6:
            formatted = f"({digits[:3]}) {digits[3:]}"
        elif 6 <= len(digits) < 10:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"

        return formatted
    
    def _fmt_ein(self, x: str | None) -> str:
        """Format an EIN string."""
        if x is None:
            return ""
        if len(x) <= 2:
            return x
        digits = re.sub(r"\D", "", x)
        formatted = f"{digits[:2]}-{digits[2:]}"
        if len(formatted) > 10:
            formatted = formatted[:11]
        return formatted
    
    def _fmt_number(self, num: str | None) -> str:
        """Format a number string, removing non-numeric characters."""
        if num is None:
            return ""
        return re.sub(r'[^0-9-/]', '', num)
    
    def _count_capitals(self, word: str) -> int:
        """Count the number of capital letters in a word."""
        return sum(1 for ch in word if ch.isupper())
    
    def _capitalize_all(self, x: str | None) -> str:
        """Capitalize all words in a string, handling acronyms."""
        if x is None:
            return "" 
        words = x.split(' ')
        for i in range(len(words)):
            if self._count_capitals(words[i]) <= 1: 
                words[i] = words[i].capitalize() if words[i].isalpha else words[i]
            if words[i].upper() in ACRONYMS: words[i] = words[i].upper()  
        result = " ".join(words)
        return result
    
    def _elim_special_chars(self, x: str | None) -> str:
        """Remove special characters from a string."""
        if x is None:
            return ""
        res = re.sub(r'[^\w\s]', '', x, flags=re.UNICODE)
        return res
    
    def _format(self, x: str | None) -> str:
        """Format a string by removing special characters and capitalizing words."""
        if x is None:
            return ""
        no_spec_chars = self._elim_special_chars(x)
        formatted = self._capitalize_all(no_spec_chars)
        return formatted
    
    def _fmt_state(self, s: str | None) -> str:
        """Format a state name to its abbreviation if available."""
        if s is None:
            return ""
        result = self._capitalize_all(s)
        result = US_STATE_ABBREVIATION.get(result, result)
        return result