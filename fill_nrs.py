import pdfrw
from pdfrw.objects.pdfstring import PdfString
import re
import fitz
import os

def insert_script_signature(pdf_path, output_path, owner_name, field_coords):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)

    rect = fitz.Rect(*field_coords["rect"])
    font_path = "data/fonts/Allura-Regular.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font not found at {font_path}")

    page.insert_textbox(
        rect,
        owner_name,
        fontfile=font_path,
        fontname='allura',
        fontsize=16,
        color=(0, 0, 0),
        align=0
    )

    doc.save(output_path)

def fill_nrs(afs_data, output_folder, bus_name):

    # Mapping AFS fields to NRS fields
    field_mapping = {
        # Business info
        "Business Legal Name": ["LegalCorporate Name"],
        "DBA": ["DBA"],
        "Entity Type": ["Type of Entity LLC INC Sole Prop"],
        "Business Start Date": ["Date Business Started"],
        "Federal Tax-I D": ["Federal Tax ID"],
        "Business Address": ["Business Address"],
        "Business City": ["City"],
        "Business State": ["State", "State of Incorporation"],
        "Business Zip": ["Zip Code"],
        "Business Description": ["Describe your Business"],
        "Annual Business Revenue": ["Monthly Gross Revenue"],
        "Average Monthly Credit Card Volume": ["CC Processing Monthly Volume"],
        "Requested Funding Amount": ["How much cash funding are you applying for"],

        # Owner info
        "Primary Owner Name": ["Corporate OfficerOwner Name", "Print Name"],
        "S S N": ["Social Sec"],
        "Date Of Birth": ["Date of Birth"],
        "Ownership %": ["Ownership"],

        # Home address (owner)
        "Home Address": ["Busin ss Address"],  # typo in form name preserved
        "Home City": ["City_2"],
        "Home State": ["State_2"],
        "Home Zip": ["Zip Code_2"],

        # Date of application
        "Date": ["Date", "Date_2"],
    }

    nrs_data = {}

    for afs_field, nrs_fields in field_mapping.items():
        afs_value = afs_data.get(afs_field, "")
        for nrs_field in nrs_fields:
            nrs_data[nrs_field] = afs_value

    nrs_data["Title"] = "CEO"

    # Fill the NRS fillable PDF
    template_path = "./data/data/NRS Funding Application.pdf"
    output_path = f"{output_folder}/NRS Funding Application - {bus_name}.pdf"
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

    # Generate scripted signature
    insert_script_signature(
        output_path, 
        f"{output_folder}/temp.pdf", 
        afs_data["Primary Owner Name"], 
        { "rect": (120, 705, 300, 805) }
    )
    os.replace(f"{output_folder}/temp.pdf", output_path)

    print("Filled NRS Application saved to:", output_path)