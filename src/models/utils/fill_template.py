import os
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfObject, PdfString

from models.utils.resource_path import resource_path
from models.utils.insert_script_signature import insert_script_signature
from models.utils.flatten_pdf import flatten_pdf_preserving_fields

def fill_pdf(afs_data: dict, output_path, template_path, sig_coords: tuple, flatten: bool):
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
                    if field:
                        field_name = field[1:-1].strip()  # strip parentheses and blanks
                        if field_name in afs_data:
                            value = afs_data[field_name]
                            if value:
                                annotation.update(PdfDict(V=PdfString.encode(value)))

    PdfWriter().write(resource_path("temp.pdf"), pdf)

    if flatten:
        flatten_pdf_preserving_fields(resource_path("temp.pdf"), output_path)
    else:
        os.replace(resource_path("temp.pdf"), output_path)

    insert_script_signature(
        output_path, 
        resource_path("temp.pdf"), 
        afs_data["Primary Owner Name"],
        sig_coords
    )
    os.replace(resource_path("temp.pdf"), output_path)

    return output_path

