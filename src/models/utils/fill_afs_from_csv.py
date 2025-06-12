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

def fill_afs_from_data(afs_data: dict, output_path):

    field_mapping = {
        # Business info
        "D B A": ["DBA"],
        "E I N": ["Federal TaxID"],
        "Business Address": ["Address"],
        "Business City": ["City"],
        "Business State": ["State"],
        "Business Zip Code": ["Zip"],

        # Owner info
        "S S N": ["SSN"],
        "Ownership %": ["Ownership"],
        "Date Of Birth": ["Date of Birth"],
        "Business Email": ["eMail"],
        "Business Phone Number": ["Phone"],
        "Email": ["Personal eMail"],
        "Cell Phone": ["Mobile Phone"],
        "Estimated Credit Score": ["Estimated FICO Score"],
        "Purpose Of Funds" : ["Purpose of Funds"],

        # Home address (owner)
        "Home Address": ["Address_2"],
        "Home City": ["City_2"],
        "Home State": ["State_2"],
        "Home Zip Code": ["Zip_2"],

        # Date of application
        "Date": ["Date"],
    }

    # for k in afs_data.keys(): print(k)

    for afs_field, template_fields in field_mapping.items():
        afs_value = afs_data.get(afs_field, "")
        for field in template_fields:
            afs_data[field] = afs_value

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

    insert_script_signature(
        output_path, 
        resource_path("temp.pdf"), 
        afs_data["Primary Owner Name"], 
        (180, 575, 360, 675)
    )
    os.replace(resource_path("temp.pdf"), output_path)

    return output_path

