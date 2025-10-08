import pprint
import pdfplumber
import re
import os
import sys
import contextlib
import csv
import pandas as pd
import datetime

from models.utils.mappings import APPLICATION_FIELD_MAPPING, CONTRACT_FIELD_MAPPING

INLINE_SUBFIELDS = [
    "DBA", "Suite/Floor", "Zip", "City", "State"
]
SECTION_HEADINGS = [
    "OWNER INFORMATION", "FUNDING INFORMATION", "BUSINESS INFORMATION"
]
CSV_KEYWORDS = [
    "Business", "Owner"
]
AGREEMENT_KEYWORDS = [
    "Agreement", "Vanguard"
]
CONTRACT_FIELDS = [
    'Merchant Name:', 'Tele No:', 'Fee:', 'EIN:', "Merchant Address:", "City:", "State:", "Zip:", 
    "Bank:", "Routing Number:", "Account Number:", "Line of Credit:", "Initial Funding:", "Print Name:", "Date:"
]
CO_OWNER_FIELDS = [
    'Co-Owner Name', 'SSN', 'Estimated FICO Score', 'Date of Birth', 'Ownership %', 'Mobile Phone', 'Personal eMail', 'Personal Fax', 
    'Address', 'City', 'State', 'Zip'
]

def normalize_key(key: str):
    return key.strip().replace(",", "").replace("\xa0", "").lower()

def map_fields(raw_data: dict, full_package: bool, field_mapping: dict[str, list[str]]):
    if full_package:
        return raw_data, None

    normalized_data = {normalize_key(k): v for k, v in raw_data.items()}
    result = {}
    missing = {}

    for out_field, input_aliases in field_mapping.items():
    # for output_fields, input_aliases in field_mapping:
        matched_value = None
        for alias in input_aliases:
            norm_alias = normalize_key(alias)
            if norm_alias in normalized_data:
                matched_value = normalized_data[norm_alias]
                break  # Stop on first match

        # for out_field in output_fields:            
        if not matched_value or matched_value.strip() == "":

            missing[out_field] = None

        # for out_field in output_fields:            
        result[out_field] = matched_value
    
    result['Date'] = datetime.date.today().strftime("%m/%d/%Y")
    print(raw_data)
    print('\n')
    print(result)
    return result, missing

def truncate_name_at_word(name, limit=40):
    if len(name) <= limit:
        return name
    trimmed = name[:limit]
    if " " in trimmed:
        return trimmed[:trimmed.rfind(" ")].rstrip()
    return trimmed.rstrip()

def clean_value(value):
    for heading in SECTION_HEADINGS:
        if heading.lower() in value.lower():
            return ""
    return value.strip()

def split_inline_fields(field, value, inline_fields):
    """Splits out known subfields that appear inline within a value."""
    subresults = {}
    for subfield in inline_fields:
        pattern = rf"\b{subfield}\s*:"
        if re.search(pattern, value):
            parts = re.split(pattern, value, maxsplit=1)
            subresults[field] = parts[0].strip()
            subresults[subfield] = parts[1].strip() if len(parts) > 1 else ""
            return subresults
    return {field: value.strip()}

def is_likely_agreement(file_path):
    try:        
        with pdfplumber.open(file_path) as pdf:
            page = pdf.pages[0]
            text = page.extract_text()
            if not text:
                return False
            for header in AGREEMENT_KEYWORDS:
                if header not in text:
                    return False
            return True
    except Exception as e:
        return False

def is_likely_application(file_path: str):
    @contextlib.contextmanager
    def suppress_stdout_stderr():
        with open(os.devnull, 'w') as fnull:
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = fnull
            sys.stderr = fnull
            try:
                yield
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
    
           
    try:
        if file_path.lower().endswith(".csv"): 
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader)
                return any(keyword.lower() in header.lower() for header in headers for keyword in CSV_KEYWORDS) 
        
        with suppress_stdout_stderr():    
            with pdfplumber.open(file_path) as pdf:
                page = pdf.pages[0]
                text = page.extract_text()
                if not text:
                    return False
                for header in SECTION_HEADINGS:
                    if header not in text:
                        return False
                return True
    except Exception as e:
        return False

def get_document_type(file_path):
    if is_likely_application(file_path):
        return "Application"
    elif is_likely_agreement(file_path):
        return "Contract"
    return None

def extract_afs_data(file_path, document_purpose):
    document_type = get_document_type(file_path)
    if not document_type:
        return None    

    field_mapping = CONTRACT_FIELD_MAPPING if document_purpose == "Contract" else APPLICATION_FIELD_MAPPING
    ext = os.path.splitext(file_path)[1]
    afs_data = {} 
    full_Package = False

    if ext == '.pdf':
        afs_data = extract_from_pdf(file_path, document_type)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
        if len(df) == 0:
            print("Empty dataframe 1")
            return None
        elif len(df) == 1:
            afs_data = extract_from_csv(file_path)
        else:
            full_Package = True
            afs_data = extract_from_full_package_csv(df)
    afs_data, missing_values = map_fields(afs_data, full_Package, field_mapping)
    # print(afs_data)
    return afs_data, missing_values, ext, full_Package

def extract_from_full_package_csv(df: pd.DataFrame):
    df.columns = df.columns.str.lower()
    if df.empty:
        print("Empty dataframe 2")
        return None
    afs_data = {}
    for i in range(0, len(df)):
        row = df.iloc[i].fillna("")
        afs_data.update({row['business name']: extract_from_df_row(row)}) 
    return afs_data
    
def extract_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    if df.empty:
        print("Empty dataframe 3")
        return None
    row = df.iloc[0].fillna("")
    return extract_from_df_row(row)

def extract_from_df_row(row):
    afs_data = {}
    matches = list(row.items())
    afs_data = extract_from_list(matches)
    afs_data['Date'] = str(datetime.date.today())
    return afs_data

def extract_from_pdf(pdf_path, document_type):
    if document_type == "Application":
        return extract_from_application(pdf_path)
    elif document_type == "Contract":
        return extract_from_contract(pdf_path)
    return None

def extract_from_contract(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    full_text = full_text.replace(' $', ':').replace('_', '').replace('M erchant', 'Merchant').replace('B ank', 'Bank')
    full_text = full_text.replace('Vanguard Capital Group', '').replace('Merchant and ACH Agreement', '')
    full_text = full_text.replace('Merchant Name: ', f"Merchant Name: {full_text[:full_text.find('Merchant Name: ')]}".replace('\n', ' '))
    full_text = " ".join([
        full_text[:full_text.find("By signing")],
        full_text[full_text.find("Line of Credit amount of"):full_text.find("for a term of")],
        full_text[full_text.find("initial funding"):full_text.find("by Alternative Funding Solutions, Inc")],
        full_text[full_text.find("Signature:"):]
    ])
    for key in CONTRACT_FIELDS:
        full_text = full_text.replace(key, f'\n{key}')
    full_text = full_text.replace('.00', '.00\n')
    # print(full_text)
    return extract_from_text(full_text)

def extract_from_application(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    start = full_text.find("BUSINESS INFORMATION")
    bus_info = full_text[
        start:
        full_text.find("OWNER INFORMATION")
    ].replace('DBA', '*DBA').replace('Fax', '*Fax')
    owner_info = full_text[
        full_text.find("OWNER INFORMATION"):
        full_text.find("CO-OWNER INFORMATION")
    ]
    co_owner_info = full_text[
        full_text.find("CO-OWNER INFORMATION"):
        full_text.find("FUNDING INFORMATION")
    ]
    funding_info = full_text[
        full_text.find("FUNDING INFORMATION"):
        full_text.find("By signing below,")
    ].replace('Description', '*Description')
    for field in CO_OWNER_FIELDS:
        co_owner_info = co_owner_info.replace(field, f"*{field}")
    full_text = " ".join([
        bus_info,
        owner_info,
        co_owner_info,
        funding_info
    ])
    full_text = full_text.replace('Personal Fax', '*Personal Fax')
    full_text = full_text.replace('Suite/Floor', '*Suite/Floor')
    full_text = full_text.replace('*', '\n*').replace('$', '')
    if start != -1:
        full_text = full_text[start:]
    return extract_from_text(full_text, categorize=True)

def extract_from_text(full_text, categorize=False):
    # Main pattern for extracting fields
    pattern = r"\*\s*(?P<field>[^:*]+?)\s*:\s*(?P<value>.*?)(?=\s*\*[^:*]+?:|\n|$)"
    matches = re.findall(pattern, full_text)
    # back up match
    if not matches:
        LABEL_VALUE = re.compile(
            r"([A-Za-z][A-Za-z /&()-]*?):\s*(.*?)(?=\s*[A-Z][A-Za-z /&()-]*?:|\n|$)",
            re.DOTALL,
        )
        matches = LABEL_VALUE.findall(full_text)

    afs_data = extract_from_list(matches, categorize=categorize)
    return afs_data

def extract_from_list(list, categorize=True):
    # Track what section we're in
    current_section = "Business"
    afs_data = {}
    for field, value in list:
        field = str(field.strip())
        value = clean_value(str(value))

        # Detect section change
        if "owner " in field.lower():
            current_section = "Owner"  # Switch context to Owner
        if "co-owner " in field.lower():
            current_section = "Co-Owner"
        if "business " in field.lower():
            current_section = "Business"

        if not categorize:
            current_section=""

        # Add section prefix to disambiguate duplicates
        normalized_field = f"{current_section} {field}" if f"{current_section.lower()} " not in field.lower() else field

        if 'Address' in normalized_field and '\n' in value:
            address = value.split('\n')[:-1]
            if len(address) == 3:
                street, city_state, zip_code = address
            else:
                street, suite, city_state, zip_code = address
                street = " ".join([street, suite])
            city, state = city_state.split(", ")
            address_mapping = {
                "Address": street, "City": city, "State": state, "Zip": zip_code
            }
            for address_field, address_value in address_mapping.items():
                afs_data.update(split_inline_fields(f"{current_section} {address_field}", address_value, INLINE_SUBFIELDS))
        else:
            afs_data.update(split_inline_fields(normalized_field, value, INLINE_SUBFIELDS))

    return afs_data

def track_missing_values(afs_data: dict):
    # Track which values were missing
    missing_values = {}

    for key, value in afs_data.items():
        if not value or value.strip() == "":
            missing_values[key] = None
    
    pprint.pprint(missing_values)

    return missing_values