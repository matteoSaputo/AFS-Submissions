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

INLINE_SUBFIELDS = [
    "DBA", "Suite/Floor", "Zip", "City", "State"
]
SECTION_HEADINGS = [
    "OWNER INFORMATION", "FUNDING INFORMATION", "BUSINESS INFORMATION"
]
CSV_HEADERS = [
    "Business Legal Name", "DBA", "Entity Type", "EIN", "Business Email", "Business Phone Number",
    "Business Fax", "Business Start Date", "Centrex ID (Hidden)", "Business Address",
    "Primary Owner Name", "Email", "Cell Phone", "SSN", "Date Of Birth",
    "Estimated Credit Score", "Ownership", "Home Address", "Business Description",
    "Purpose of Funds", "Annual Business Revenue", "Requested Funding Amount",
    "Average Monthly Credit Card Volume", "Outstanding Receivables", "Upload your statements here"
]
FULL_PACKAGE_HEADERS = [
    "BUSINESS NAME", "TAX ID", "BUSINESS START DATE", "PHONE", "Mobile 1", "Mobile 2", "Email 1", 
    "Email 2", "Email 3", "SSN", "OWNER NAME", "DATE OF BIRTH", "ADDRESS,", "CITY,", "STATE,", "Business Zip", "MONTHLY REVENUE", 
    "Date", "Zip", "S S N"
]
TODAY = str(datetime.date.today())

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
                lower_headers = [h.lower() for h in headers]
                lower_csv_headers = [h.lower() for h in CSV_HEADERS]
                lower_fp_headers = [h.lower() for h in FULL_PACKAGE_HEADERS]
                return all(h.lower() in lower_csv_headers for h in lower_headers) or all(h.lower() in lower_fp_headers for h in lower_headers)
        
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
    except Exception:
        return False

def extract_afs_data(file_path):
    if not is_likely_application(file_path):
        return None
    ext = os.path.splitext(file_path)[1]
    afs_data = {} 
    missing_values = {}
    full_Package = False

    if ext == '.pdf':
        afs_data, missing_values = extract_from_pdf(file_path)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
        if len(df) == 0: 
            return None
        elif len(df) == 1:
            afs_data, missing_values = extract_from_csv(file_path)
        else:
            full_Package = True
            df.columns = df.columns.str.lower()
            afs_data, missing_values = extract_from_full_package_csv(df)
    return afs_data, missing_values, ext, full_Package

def extract_from_full_package_csv(df: pd.DataFrame):
    if df.empty:
        return None
    afs_data = {}
    for i in range(0, len(df)):
        row = df.iloc[i].fillna("")
        afs_data.update({row['business name']: extract_from_df_row(row)}) 
    # pprint.pprint(afs_data)
    return afs_data, None
    
def extract_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    if df.empty:
        return None
    row = df.iloc[0].fillna("")
    return extract_from_df_row(row)

def extract_from_df_row(row):
    afs_data = {}
    matches = list(row.items())
    afs_data = extract_from_list(matches)
    afs_data['Date'] = TODAY
    return afs_data, track_missing_values(afs_data)

def extract_from_pdf(pdf_path):
    if not is_likely_application(pdf_path):
        return None
    
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    start = full_text.find("BUSINESS INFORMATION")
    if start != -1:
        full_text = full_text[start:]

    # Main pattern for extracting fields
    pattern = r"\*\s*(?P<field>[^:*]+?)\s*:\s*(?P<value>.*?)(?=\s*\*[^:*]+?:|\n|$)"
    matches = re.findall(pattern, full_text)

    afs_data = extract_from_list(matches)

    # Limit Business Name to 30 characters
    afs_data["Business Legal Name"] = truncate_name_at_word(afs_data["Business Legal Name"])

    afs_data['Date'] = TODAY

    return afs_data, track_missing_values(afs_data)

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
            street, city_state, zip_code = address
            city, state = city_state.split(", ")
            address_mapping = {
                "Address": street, "City": city, "State": state, "Zip": zip_code
            }
            for address_field, address_value in address_mapping.items():
                afs_data.update(split_inline_fields(f"{current_section} {address_field}", address_value, INLINE_SUBFIELDS))
            continue

        afs_data.update(split_inline_fields(normalized_field, value, INLINE_SUBFIELDS))
    return afs_data

def track_missing_values(afs_data):
    # Track which values were missing
    missing_values = {}

    # Handle missing SSN
    if (not afs_data.get("S S N") or afs_data["S S N"].strip() == "") and (not afs_data.get("SSN") or afs_data["SSN"].strip() == "") and (not afs_data.get("Ssn") or afs_data["Ssn"].strip() == ""):
        afs_data["S S N"] = f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"
        missing_values["S S N"] = afs_data["S S N"]
        afs_data["Ssn"] = f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"
        missing_values["Ssn"] = afs_data["Ssn"]

    # Handle missing Date of Birth
    if not afs_data.get("Date Of Birth") or afs_data["Date Of Birth"].strip() == "":
        afs_data["Date Of Birth"] = "01/01/1980"
        missing_values["Date Of Birth"] = afs_data["Date Of Birth"]

    # Handle missing Business Start Date
    if not afs_data.get("Business Start Date") or afs_data["Business Start Date"].strip() == "":
        afs_data["Business Start Date"] = "01/01/2020"
        missing_values["Business Start Date"] = afs_data["Business Start Date"]

    return missing_values