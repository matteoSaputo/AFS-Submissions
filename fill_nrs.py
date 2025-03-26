from afs_parser import extract_afs_data
import pdfrw

# Step 1: Extract data from the AFS Application
afs_data = extract_afs_data("AFS Application.pdf")

print(afs_data)

mapping = {
    "Business Legal Name": "LegalCorporate Name",
    "DBA": "DBA",
    "Address": "Business Address",
    "Suite/Floor": "Suite/Floor",
    "City": "City",
    "State": "State",
    "Zip": "Zip Code",
    "Federal Tax-ID": "Federal Tax ID",
    "Primary Owner Name": "Corporate OfficerOwner Name",
    "SSN": "Social Sec",
    "Date of Birth": "Date of Birth",
    "Ownership %": "Ownership",
    "Estimated FICO Score": "Estimated FICO Score",  
    "Business Description": "Describe your Business",
    "Purpose of Funds": "Purpose of Funds",
    "Requested Funding Amount": "How much cash funding are you applying for",
    "Annual Business Revenue": "Monthly Gross Revenue",
    "Average Monthly Credit Card Volume": "CC Processing Monthly Volume",
    "Outstanding Receivables": "Outstanding Receivables",
    "Date": "Date"
}

nrs_data = {nrs_field: afs_data.get(afs_field, "") for afs_field, nrs_field in mapping.items()}

# Step 3: Fill the NRS fillable PDF
template_path = "NRS Funding Application.pdf"
output_path = "Filled_NRS_Funding_Application.pdf"
template_pdf = pdfrw.PdfReader(template_path)

# Make sure appearance updates
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
print("✅ Filled NRS Application saved to:", output_path)