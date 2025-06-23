import os
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfObject, PdfString, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import io

from models.utils.resource_path import resource_path
from models.utils.insert_script_signature import insert_script_signature


def flatten_pdf_preserving_fields(input_path, output_path):
    pdfmetrics.registerFont(TTFont("lucida-console", resource_path("data/fonts/LUCON.TTF")))

    # Load PDF and read form values
    template_pdf = PdfReader(input_path)
    overlays = []

    for page in template_pdf.pages:
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        if page.Annots:
            for annot in page.Annots:
                if annot.Subtype == '/Widget' and annot.T and annot.V:
                    key = annot.T[1:-1]
                    value = annot.V.to_unicode() if hasattr(annot.V, 'to_unicode') else str(annot.V)
                    rect = annot.Rect
                    x, y = float(rect[0]), float(rect[1])

                    can.setFont("lucida-console", 9)
                    can.drawString(x + 3, y + 4, value)

        can.save()
        packet.seek(0)
        overlay_pdf = PdfReader(packet)
        overlays.append(overlay_pdf.pages[0])

    # Merge text overlays into the original pages
    for i, page in enumerate(template_pdf.pages):
        PageMerge(page).add(overlays[i]).render()
        page.Annots = []  # remove interactive fields

    PdfWriter().write(output_path, template_pdf)

def normalize_key(key: str):
    return key.strip().replace(",", "").replace("\xa0", "").lower()

def map_afs_fields(afs_data_raw, field_mapping):
    # Normalize keys
    normalized_data = {
        normalize_key(k): v for k, v in afs_data_raw.items()
    }

    afs_data = {}
    for target_field, possible_keys in field_mapping.items():
        for key in possible_keys:
            if normalize_key(key) in normalized_data:
                afs_data[target_field] = normalized_data[normalize_key(key)]
                break  # stop at first match
    return afs_data

def fill_afs_from_data(afs_data: dict, output_path):

    # field_mapping = {
    #     # Business info
    #     "Business Name": ["Business Legal Name"],
    #     "D B A": ["DBA"],
    #     # "E I N": ["Federal TaxID"],
    #     "Tax Id": ["Federal TaxID"],
    #     "Business Address": ["Address"],
    #     "Business City": ["City"],
    #     "Business State": ["State"],
    #     "Business Zip": ["Zip"],
    #     "Address,": ["Address"],
    #     "City,": ["City"],
    #     "State,": ["State"],
    #     "Business Zip": ["Zip"],
    #     "Monthly Revenue": ["Monthly Gross Revenue"],

    #     # Owner info
    #     "Owner Name": ["Primary Owner Name"],
    #     "S S N": ["SSN"],
    #     "SSN" : ["SSN"],
    #     "Ssn" : ["SSN"],
    #     "Ownership": ["Ownership %"],
    #     "Date Of Birth": ["Date of Birth"],
    #     "Business Email": ["eMail"],
    #     "Email 1": ["eMail"],
    #     # "Business Phone Number": ["Phone"],
    #     "Email": ["Personal eMail"],
    #     "Email 2": ["Personal eMail"],
    #     "Email 3": ["Personal Fax"],
    #     "Mobile 1": ["Fax"],
    #     "Mobile 2": ["Mobile Phone"],
    #     "Estimated Credit Score": ["Estimated FICO Score"],
    #     "Purpose Of Funds" : ["Purpose of Funds"],

    #     # Home address (owner)
    #     "Home Address": ["Address_2"],
    #     "Home City": ["City_2"],
    #     "Home State": ["State_2"],
    #     "Home Zip": ["Zip_2"],

    #     # Date of application
    #     "Date": ["Date"],
    # }

    # for k in afs_data.keys(): print(k)

    field_mapping = {
        "Business Legal Name": ["business name", "business legal name"],
        "DBA": ["dba"],
        "Federal TaxID": ["tax id", "ein", "e i n", "federal tax-id", "federal taxid", "federal tax id"],
        "Address": ["business address", "address", "address,"],
        "City": ["city", "city,", "business city", "business city,"],
        "State": ["state", "state,", "business state", "business state,"],
        "Zip": ["zip", "business zip"],
        "Business Start Date" : ["business start date", "start date"],
        "Monthly Gross Revenue": ["monthly revenue", "annual business revenue"],
        "Primary Owner Name": ["owner name", "primary owner name"],
        "SSN": ["ssn", "ssn ", "ssn  ", "s s n", "social", "social security number"],
        "Ownership %": ["ownership"],
        "Date of Birth": ["date of birth"],
        "eMail": ["business email", "email 1"],
        "Personal eMail": ["email", "email 2"],
        "Personal Fax": ["email 3"],
        "Fax": ["mobile 1"],
        "Mobile Phone": ["mobile 2", "cell phone"],
        "Estimated FICO Score": ["estimated credit score"],
        "Purpose of Funds": ["purpose of funds"],
        "Address_2": ["home address"],
        "City_2": ["home city"],
        "State_2": ["home state"],
        "Zip_2": ["home zip"],
        "Date": ["date"],
    }


    afs_data = map_afs_fields(afs_data, field_mapping)

    pdf = PdfReader("data\data\AFS Application (Fillable).pdf")
    if pdf.Root.AcroForm:
        pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))

    for page in pdf.pages:
        annotations = page.get('/Annots')
        if annotations:
            for annotation in annotations:
                if annotation['/Subtype'] == '/Widget':
                    field = annotation.get('/T')
                    if field:
                        field_name = field[1:-1].strip()  # strip parentheses and blanks
                        if field_name in afs_data:
                            value = afs_data[field_name]
                            annotation.update(PdfDict(V=PdfString.encode(value)))

    PdfWriter().write(resource_path("temp.pdf"), pdf)

    flatten_pdf_preserving_fields(resource_path("temp.pdf"), output_path)

    owner_name = afs_data["Primary Owner Name"] if afs_data.get("Primary Owner Name") else afs_data["Owner Name"]


    insert_script_signature(
        output_path, 
        resource_path("temp.pdf"), 
        owner_name,
        (180, 575, 360, 675)
    )
    os.replace(resource_path("temp.pdf"), output_path)

    return output_path

