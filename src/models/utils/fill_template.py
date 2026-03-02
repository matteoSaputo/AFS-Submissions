"""
fill_template: Utility for filling PDF templates with AFS data.

Uses pdfrw to fill form fields in PDF templates, optionally flattens and signs the output.
"""

import os
import re
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfObject, PdfString
import pprint

from models.utils.resource_path import resource_path
from models.utils.insert_script_signature import insert_script_signature
from models.utils.flatten_pdf import flatten_pdf_preserving_fields

def fill_pdf(afs_data: dict, output_path, template_path, signature="", sig_coords=(0, 0, 0, 0), flatten=False, sign=True):
    """Fill a PDF template with AFS data and optionally flatten/sign.

    Parameters
    ----------
    afs_data : dict
        Data to fill into the PDF form fields.
    output_path : str
        Path to save the filled PDF file.
    template_path : str
        Path to the PDF template file.
    signature : str, optional
        Signature to insert (default: empty string).
    sig_coords : tuple, optional
        Coordinates for signature placement (default: (0, 0, 0, 0)).
    flatten : bool, optional
        Whether to flatten the PDF after filling (default: False).
    sign : bool, optional
        Whether to sign the PDF after filling (default: True).
    """
    if os.path.exists(output_path):
        os.unlink(output_path)

    pdf = PdfReader(template_path)
    if pdf.Root.AcroForm:
        pdf.Root.AcroForm.update(PdfDict(NeedAppearances=PdfObject('true')))
    for page in pdf.pages:
        annotations = page.get('/Annots')
        if annotations:
            for annotation in annotations:
                if annotation['/Subtype'] == '/Widget':
                    field = annotation.get('/T')
                    if not field:
                        field = annotation.get('/Parent').get('/T')
                    if field: 
                        field_name = field[1:-1].strip() # strip parentheses and blanks
                        if field_name in afs_data:
                            value = afs_data[field_name]
                            if value:
                                annotation.update(PdfDict(V=PdfString.encode(value)))

    PdfWriter().write(resource_path("temp.pdf"), pdf)

    if flatten:
        flatten_pdf_preserving_fields(resource_path("temp.pdf"), output_path)
    else:
        os.rename(resource_path("temp.pdf"), output_path)

    if sign:
        insert_script_signature(
            output_path, 
            resource_path("temp.pdf"), 
            signature,
            sig_coords
        )
        os.replace(resource_path("temp.pdf"), output_path)

    # Clean up
    if os.path.exists(resource_path("temp.pdf")):
        os.remove(resource_path("temp.pdf"))

    return output_path