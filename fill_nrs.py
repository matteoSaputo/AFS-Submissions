from afs_parser import extract_afs_data
import pdfrw

# Extract data from the AFS Application
afs_data = extract_afs_data("Business Application.pdf")

print(afs_data)

mapping = {
    "Business Legal Name": "LegalCorporate Name",
    "DBA": "DBA",
    "Entity Type": "Type of Entity LLC INC Sole Prop",
    "Business Start Date": "Date Business Started",
    "Federal Tax-ID": "Federal Tax ID",
    "Address": "Business Address",
    "City": "City",
    "State": "State",
    "Zip": "Zip Code",
    "Business Description": "Describe your Business",
    "Annual Business Revenue": "Monthly Gross Revenue",
    "Average Monthly Credit Card Volume": "CC Processing Monthly Volume",
    "Primary Owner Name": "Corporate OfficerOwner Name",
    "Ownership %": "Ownership",
    "Date of Birth": "Date of Birth",
    "SSN": "Social Sec",
    "Requested Funding Amount": "How much cash funding are you applying for",
    "Date": "Date",
}


nrs_data = {nrs_field: afs_data.get(afs_field, "") for afs_field, nrs_field in mapping.items()}

# Fill the NRS fillable PDF
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