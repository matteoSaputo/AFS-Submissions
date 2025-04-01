import pdfplumber
import re

def extract_afs_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    # Narrow scope to avoid Docusign garbage
    start = full_text.find("BUSINESS INFORMATION")
    if start != -1:
        full_text = full_text[start:]

    # Base regex pattern: * Field: Value
    pattern = r"\*\s*(?P<field>[^:*]+?)\s*:\s*(?P<value>.*?)(?=\s*\*[^:*]+?:|\n|$)"
    matches = re.findall(pattern, full_text)

    INLINE_SUBFIELDS = [
        "DBA", "Suite/Floor", "Fax", "Personal eMail", "Personal Fax", "Zip", "City", "State"
    ]

    def split_inline_fields(field, value, inline_fields):
        """Splits out known subfields that appear inline within a value."""
        subresults = {}

        # Loop through all known inline field names
        for subfield in inline_fields:
            pattern = rf"\b{subfield}\s*:"
            if re.search(pattern, value):
                # Split on subfield and recursively split remaining text
                parts = re.split(pattern, value, maxsplit=1)
                subresults[field] = parts[0].strip()
                subresults[subfield] = parts[1].strip() if len(parts) > 1 else ""
                return subresults  # return early after first match

        # If no inline subfield is found
        return {field: value.strip()}


    afs_data = {}
    for field, value in matches:
        field = field.strip()
        value = value.strip()

        # Attempt to split any inline subfields within the value
        split_data = split_inline_fields(field, value, INLINE_SUBFIELDS)

        # Merge the result into afs_data
        afs_data.update(split_data)

    lines = full_text.splitlines()
    for idx, line in enumerate(lines):
        if "*Date:" in line:
            # Look one line above it
            if idx > 0:
                possible_date = lines[idx - 1].strip()
                # Check if it's a date-like string
                if re.match(r"\d{1,2}/\d{1,2}/\d{4}", possible_date):
                    afs_data["Date"] = possible_date
                else:
                    afs_data["Date"] = "Not Found"
            break
    else:
        afs_data["Date"] = "Not Found"

    return afs_data


# Extract the data
afs_data = extract_afs_data("AFS Application.pdf")

# Print it nicely
print("✅ Cleaned Extracted AFS Data:")
for key, value in afs_data.items():
    print(f"{key}::: {value}\n")
