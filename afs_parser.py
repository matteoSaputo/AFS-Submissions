import pdfplumber
import re
import random
import fitz
import os

from resource_path import resource_path

INLINE_SUBFIELDS = [
    "DBA", "Suite/Floor", "Zip", "City", "State"
]
SECTION_HEADINGS = [
    "OWNER INFORMATION", "FUNDING INFORMATION", "BUSINESS INFORMATION", "ATTACH", "By signing below",
]

def normalize_field_name(field):
    # Insert space before capital letters that follow lowercase or other capitals
    spaced = re.sub(r'(?<=[a-zA-Z])(?=[A-Z])', ' ', field)
    return spaced.strip().title()

def overlay_afs_fields(input_path, output_path, afs_data):
    doc = fitz.open(input_path)
    page = doc[0]  # Assuming all data is on page 1

    # Define positions
    field_coords = {
        "S S N": (65, 280),                 
        "Date Of Birth": (305, 280),
        "Business Start Date": (325, 180)
    }

    # Load the custom Lucida Console font
    font_path = resource_path("./data/fonts/LUCON.TTF")

    # Font settings
    font_size = 9
    font_color = (0, 0, 0)  # Black

    for field, value in afs_data.items():
        if field in field_coords and value.strip():
            x, y = field_coords[field]
            # Use insert_textbox to allow font embedding
            rect = fitz.Rect(x, y, x + 200, y + 15)  # Adjust width/height as needed
            page.insert_textbox(
                rect,
                value,
                fontname="lucida-console",     
                fontfile=font_path,          
                fontsize=font_size,
                color=font_color,
                align=0  # left-align
            )

    doc.save(output_path)

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

def extract_special_field_from_lines(lines, target_field="*Date:", field_name="Date"):
    """Handles special case where the field value (e.g., a date) appears on the line above its label."""
    for idx, line in enumerate(lines):
        if target_field in line:
            if idx > 0:
                possible_value = lines[idx - 1].strip()
                if re.match(r"\d{1,2}/\d{1,2}/\d{4}", possible_value):
                    return field_name, possible_value
            break
    return field_name, "Not Found"

def extract_afs_data(pdf_path):
    """Main function to extract cleaned AFS application data from a PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    start = full_text.find("BUSINESS INFORMATION")
    if start != -1:
        full_text = full_text[start:]

    # Track what section we're in
    current_section = "Business"

    # Main pattern for extracting fields
    pattern = r"\*\s*(?P<field>[^:*]+?)\s*:\s*(?P<value>.*?)(?=\s*\*[^:*]+?:|\n|$)"
    matches = re.findall(pattern, full_text)

    afs_data = {}
    for field, value in matches:
        field = normalize_field_name(field.strip())
        value = clean_value(value)

        # Detect section change
        if field.lower() == "primary owner name":
            current_section = "Home"  # Switch context to Owner/Home

        # Add section prefix to disambiguate duplicates
        normalized_field = f"{current_section} {field}" if field in ["Address", "City", "State", "Zip"] else field

        afs_data.update(split_inline_fields(normalized_field, value, INLINE_SUBFIELDS))

    # Limit Business Name to 30 characters
    afs_data["Business Legal Name"] = truncate_name_at_word(afs_data["Business Legal Name"])

    # Track which values were missing
    missing_values = {}

    # Handle missing SSN
    if not afs_data.get("S S N") or afs_data["S S N"].strip() == '':
        afs_data["S S N"] = f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}"
        missing_values["S S N"] = afs_data["S S N"]

    # Handle missing Date of Birth
    if not afs_data.get("Date Of Birth") or afs_data["Date Of Birth"].strip() == "":
        afs_data["Date Of Birth"] = "01/01/1980"
        missing_values["Date Of Birth"] = afs_data["Date Of Birth"]

    # Handle missing Business Start Date
    if not afs_data.get("Business Start Date") or afs_data["Business Start Date"].strip() == "":
        afs_data["Business Start Date"] = "01/01/2020"
        missing_values["Business Start Date"] = afs_data["Business Start Date"]

    # Generate missing values
    overlay_afs_fields(pdf_path, "temp_overlay.pdf", missing_values)
    os.replace("temp_overlay.pdf", pdf_path)

    # Special fix for "Date"
    lines = full_text.splitlines()
    date_field, date_value = extract_special_field_from_lines(lines)
    afs_data[date_field] = date_value

    return afs_data
