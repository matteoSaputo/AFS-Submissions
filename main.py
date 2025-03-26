import pdfplumber
import re
import pdfrw

def extract_afs_data(pdf_path):
    """Extracts key business and owner information from the AFS Application PDF."""
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"  # Append text from all pages

    start_index = full_text.find("BUSINESS INFORMATION")
    if start_index != -1:
        full_text = full_text[start_index:]

    pattern = r'\*(?P<field>[^:]+):\s*(?P<value>.*?)(?=\s*\*|$)'
    matches = re.findall(pattern, full_text, re.DOTALL)

    afs_data = {field.strip(): value.strip() for field, value in matches}
    return afs_data

# Extract AFS Data
afs_data = extract_afs_data("AFS Application.pdf")
print(afs_data)

# Mapping AFS fields to NRS fields
afs_to_nrs_mapping = {
    "*Business Legal Name": "LegalCorporate Name",
    "Business Address": "Business Address",
    "Business Start Date": "Date Business Started",
    "Federal Tax-ID": "Federal Tax ID",
    "Primary Owner Name": "Corporate OfficerOwner Name",
    "Ownership %": "Ownership",
    "Date of Birth": "Date of Birth",
    "SSN": "Social Sec",
    "Requested Funding Amount": "How much cash funding are you applying for",
    "Annual Business Revenue": "Monthly Gross Revenue"
}

nrs_data = {nrs_field: afs_data.get(afs_field, "Not Found") for afs_field, nrs_field in afs_to_nrs_mapping.items()}

# Fill NRS Application
template_path = "NRS Funding Application.pdf"
output_path = "Filled_NRS_Funding_Application.pdf"
template_pdf = pdfrw.PdfReader(template_path)

if template_pdf.Root.AcroForm:
    template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))

for page in template_pdf.pages:
    annotations = page.get('/Annots')
    if annotations:
        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget':
                field = annotation.get('/T')
                if field:
                    field_name = field[1:-1]
                    if field_name in nrs_data:
                        annotation.update(pdfrw.PdfDict(V=nrs_data[field_name]))

pdfrw.PdfWriter().write(output_path, template_pdf)
print("✅ Successfully extracted and filled NRS Application!")
