import fitz  # PyMuPDF
import os
import io

from pdfrw import PdfReader, PdfWriter, PageMerge
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from models.utils.resource_path import resource_path

def flatten_pdf(input_path, output_path):
    doc = fitz.open(input_path)
    new_doc = fitz.open()

    for page in doc:
        # Create a new page with the same dimensions
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)

        # Copy contents from original to new page
        new_page.show_pdf_page(page.rect, doc, page.number)

    new_doc.save(resource_path("temp.pdf"))
    doc.close()
    new_doc.close()

    os.remove(input_path)
    os.rename(resource_path("temp.pdf"), output_path)
    print(f"Flattened Business App saved to: {output_path}")

    return output_path

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
