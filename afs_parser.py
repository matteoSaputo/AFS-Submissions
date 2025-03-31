import pdfplumber
import re

INLINE_SUBFIELDS = [
    "DBA", "Suite/Floor", "Fax", "Personal eMail", "Personal Fax", "Zip", "City", "State"
]

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
        field = field.strip()
        value = value.strip()

        # Detect section change
        if field.lower() == "primary owner name":
            current_section = "Home"  # Switch context to Owner/Home

        # Add section prefix to disambiguate duplicates
        normalized_field = f"{current_section} {field}" if field in ["Address", "City", "State", "Zip"] else field

        afs_data.update(split_inline_fields(normalized_field, value, INLINE_SUBFIELDS))

    # Special fix for "Date"
    lines = full_text.splitlines()
    date_field, date_value = extract_special_field_from_lines(lines)
    afs_data[date_field] = date_value

    return afs_data
