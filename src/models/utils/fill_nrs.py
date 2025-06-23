import pdfrw
from pdfrw.objects.pdfstring import PdfString

import os

from models.utils.resource_path import resource_path
from models.utils.insert_script_signature import insert_script_signature

def normalize_key(key: str):
    return key.strip().replace(",", "").replace("\xa0", "").lower()

def map_nrs_fields(raw_data, field_map):
    norm = {normalize_key(k): v for k, v in raw_data.items()}

    result = {}
    for nrs_field, candidates in field_map.items():
        for c in candidates:
            if normalize_key(c) in norm:
                result[nrs_field] = norm[normalize_key(c)]
                break
    result["Title"] = "CEO"
    return result


def fill_nrs(afs_data, output_path):
    if os.path.exists(output_path):
        os.unlink(output_path)

    state = afs_data.get("Business State", afs_data.get("State,", ""))
    if state.lower() in ['ca', 'california', 'cali', 'va', 'virginia']:
        return None

    # Mapping AFS fields to NRS fields
    # field_mapping = {
    #     # Business info
    #     "Business Legal Name": ["LegalCorporate Name"],
    #     "DBA": ["DBA"],
    #     "Entity Type": ["Type of Entity LLC INC Sole Prop"],
    #     "Business Start Date": ["Date Business Started"],
    #     # "Federal Tax-I D": ["Federal Tax ID"],
    #     "Tax Id": ["Federal Tax ID"],
    #     # "Business Address": ["Business Address"],
    #     "Business City": ["City"],
    #     "Business State": ["State", "State of Incorporation"],
    #     "Business Zip": ["Zip Code"],
    #     "Business Description": ["Describe your Business"],
    #     "Annual Business Revenue": ["Monthly Gross Revenue"],
    #     "Average Monthly Credit Card Volume": ["CC Processing Monthly Volume"],
    #     "Requested Funding Amount": ["How much cash funding are you applying for"],
    #     "Address,": ["Business Address"],
    #     "City,": ["City"],
    #     "State,": ["State", "State of Incorporation"],

    #     # Owner info
    #     "Primary Owner Name": ["Corporate OfficerOwner Name", "Print Name"],
    #     # "S S N": ["Social Sec"],
    #     "Ssn" : ["Social Sec"],
    #     "Date Of Birth": ["Date of Birth"],
    #     "Ownership %": ["Ownership"],

    #     # Home address (owner)
    #     "Home Address": ["Busin ss Address"],  # typo in form name preserved
    #     "Home City": ["City_2"],
    #     "Home State": ["State_2"],
    #     "Home Zip": ["Zip Code_2"],

    #     # Date of application
    #     "Date": ["Date", "Date_2"],
    # }

    field_mapping = {
        "LegalCorporate Name": ["business name", "business legal name"],
        "DBA": ["dba"],
        "Type of Entity LLC INC Sole Prop": ["entity type"],
        "Date Business Started": ["business start date", "start date"],
        "Federal Tax ID": ["tax id", "ein", "e i n", "federal tax-id", "federal taxid", "federal tax id"],

        "Business Address": ["business address", "address", "address,"],
        "City": ["business city", "city", "city,"],
        "State": ["business state", "state", "state,"],
        "State of Incorporation": ["business state", "state", "state,"],
        "Zip Code": ["business zip", "zip"],

        "Describe your Business": ["business description"],
        "Monthly Gross Revenue": ["annual business revenue", "monthly revenue"],
        "CC Processing Monthly Volume": ["average monthly credit card volume"],
        "How much cash funding are you applying for": ["requested funding amount"],

        "Corporate OfficerOwner Name": ["owner name", "primary owner name"],
        "Print Name": ["owner name", "primary owner name"],
        "Social Sec": ["ssn", "ssn ", "ssn  ", "s s n", "social", "social security number"],
        "Date of Birth": ["date of birth", "dob", "d o b"],
        "Ownership": ["ownership", "ownership %"],

        "Busin ss Address": ["home address", "home address,"],  # typo in NRS PDF
        "City_2": ["home city", "home city,"],
        "State_2": ["home state", "home state,"],
        "Zip Code_2": ["home zip","home zip,"],

        "Date": ["date"],
        "Date_2": ["date"]
    }

    nrs_data = map_nrs_fields(afs_data, field_mapping)

    # Fill the NRS fillable PDF
    template_path = resource_path("data/data/NRS Funding Application.pdf")
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
                        field_name = field[1:-1]  # strip parentheses
                        if field_name in nrs_data:
                            value = nrs_data[field_name]
                            annotation.update(pdfrw.PdfDict(V=PdfString.encode(value)))
    pdfrw.PdfWriter().write(output_path, template_pdf)

    owner_name = afs_data["Primary Owner Name"] if afs_data.get("Primary Owner Name") else afs_data["Owner Name"]

    # Generate scripted signature
    insert_script_signature(
        output_path, 
        resource_path("temp.pdf"), 
        owner_name, 
        (120, 705, 300, 805)
    )
    os.replace(resource_path("temp.pdf"), output_path)

    print("Filled NRS Application saved to:", output_path)
    return output_path