import pprint
import pdfplumber
import re
import random
import os
import sys
import contextlib
import csv
import pandas as pd
import datetime

TODAY = str(datetime.date.today())
INLINE_SUBFIELDS = [
    "DBA", "Suite/Floor", "Zip", "City", "State"
]
SECTION_HEADINGS = [
    "OWNER INFORMATION", "FUNDING INFORMATION", "BUSINESS INFORMATION"
]
CSV_KEYWORDS = [
    "Business", "Owner"
]
FIELD_MAPPING = [
    (["Business Legal Name", "LegalCorporate Name"], ["business name", "business legal name"]),
    (["DBA", "DBA Name"], ["dba"]),
    (["Entity Type", "Type of Entity LLC INC Sole Prop", "Legal Entity Type"], ["entity type"]),
    (["Federal TaxID", "Federal Tax ID"], ["tax id", "ein", "e i n", "federal tax-id", "federal taxid", "federal tax id", "federal tax-i d", "federal tax i d"]),
    (["Address", "Business Address", "Corporate Legal Address"], ["business address", "address", "address,", "business address street", "address street", "address street,", "business address: address line 1"]),
    (["City"], ["city", "city,", "business city", "business city,", "business address: city"]),
    (["State", "State of Incorporation", "State of Organization"], ["state", "state,", "business state", "business state,", "business address: state"]),
    (["Zip", "Zip Code"], ["zip", "business zip", "business address: zip/postal code"]),
    (["Business Start Date", "Date Business Started", "Date of Organization"], ["business start date", "start date"]),
    (["Primary Owner Name", "Corporate OfficerOwner Name", "Print Name", "Name of Officer Signing Application", "Name of Principal OwnerGuarantor"], ["owner name", "primary owner name", "primary owner name: first"]),
    (["SSN", "Social Sec", "Social Security Number"], ["ssn", "ssn ", "ssn  ", "s s n", "social", "social security number"]),
    (["Ownership %", "Ownership"], ["ownership", "ownership %"]),
    (["Date of Birth", "Date Of Birth"], ["date of birth", "birth date"]),
    (["eMail"], ["business email", "email 1"]),
    (["Personal eMail"], ["email", "email 2"]),
    (["Personal Fax"], ["email 3"]),
    (["Fax"], ["mobile 1"]),
    (["Phone"], ["mobile"]),
    (["Mobile Phone"], ["mobile 2", "cell phone"]),
    (["Estimated FICO Score"], ["estimated credit score"]),
    (["Purpose of Funds"], ["purpose of funds"]),
    (["Address_2", "Busin ss Address", "Home Address"], ["home address", "home address,", "home address street", "home address street,", "home address: address line 1"]),
    (["City_2"], ["home city", "home address: city"]),
    (["State_2"], ["home state", "home address: state"]),
    (["Zip_2", "Zip Code_2"], ["home zip", "home address: zip/postal Code"]),
    (["Date", "Date_2"], ["date"]),
    (["Business Description", "Describe your Business", "Type of Business"], ["business description"]),
    (["Monthly Gross Revenue", "Annual Business Revenue", "Total Annual Sales"], ["monthly revenue", "annual business revenue"]),
    (["Requested Funding Amount", "How much cash funding are you applying for", "Total Cash Needed"], ["requested funding amount"]),
    (["Average Monthly Credit Card Volume", "CC Processing Monthly Volume"], ["average monthly credit card volume"]),
    (["Outstanding Receivables"], ["outstanding receivables"])
]
DEFAULT_VALUES = {
    "SSN": f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}",
    "Date of Birth": "01/01/1980",
    "Business Start Date": "01/01/2020" 
}

def normalize_key(key: str):
    return key.strip().replace(",", "").replace("\xa0", "").lower()

def map_fields(raw_data: dict, full_package: bool):
    if full_package:
        return raw_data, None

    normalized_data = {normalize_key(k): v for k, v in raw_data.items()}
    result = {}
    missing = {}

    for output_fields, input_aliases in FIELD_MAPPING:
        matched_value = None
        for alias in input_aliases:
            norm_alias = normalize_key(alias)
            if norm_alias in normalized_data:
                matched_value = normalized_data[norm_alias]
                break  # Stop on first match

        for out_field in output_fields:            
            if not matched_value or matched_value.strip() == "":
                matched_value = DEFAULT_VALUES.get(out_field, None)
                missing[out_field] = DEFAULT_VALUES.get(out_field, None)

        for out_field in output_fields:            
            result[out_field] = matched_value
    
    result["Business Legal Name"] = truncate_name_at_word(result.get("Business Legal Name", " "))
    result['Date'] = TODAY
    result["Title"] = "CEO"
    result["Primary Owner Name"] = f"{result.get('Primary Owner Name', '')} {raw_data.get('Primary Owner Name: Last', '')}"


    return result, missing

def normalize_field_name(field):
    # Insert space before capital letters that follow lowercase or other capitals
    spaced = re.sub(r'(?<=[a-zA-Z])(?=[A-Z])', ' ', field)
    return spaced.strip().title()

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
    return value.strip().replace('_', '')

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

def is_likely_application(file_path):
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
                    print("no text")
                    return False
                for header in SECTION_HEADINGS:
                    if header not in text:
                        print(header)
                        return False
                return True
    except Exception as e:
        print(e)
        return False

def extract_afs_data(file_path):
    if not is_likely_application(file_path):
        print("Not likely Application")
        return None
    ext = os.path.splitext(file_path)[1]
    afs_data = {} 
    full_Package = False

    if ext == '.pdf':
        afs_data = extract_from_pdf(file_path)
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
    afs_data, missing_values = map_fields(afs_data, full_Package)
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
    afs_data['Date'] = TODAY
    return afs_data

def extract_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    full_text = full_text.replace(' $', ':')
    start = full_text.find("BUSINESS INFORMATION")
    if start != -1:
        full_text = full_text[start:]
    print(full_text)
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

    afs_data = extract_from_list(matches)

    return afs_data

def extract_from_list(list):
    # Track what section we're in
    current_section = "Business"

    afs_data = {}
    for field, value in list:
        field = normalize_field_name(str(field.strip()))
        value = clean_value(str(value))

        # Detect section change
        if field.lower() == "primary owner name":
            current_section = "Home"  # Switch context to Owner/Home

        # Add section prefix to disambiguate duplicates
        normalized_field = f"{current_section} {field}" if field in ["Address", "City", "State", "Zip"] else field

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