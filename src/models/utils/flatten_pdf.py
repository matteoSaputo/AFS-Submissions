"""
flatten_pdf: Utilities for flattening PDF files and preserving form fields.

Provides functions to flatten PDFs using PyMuPDF and pdfrw, and to preserve form field data and fonts.
"""

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
    """Flatten a PDF file, removing form fields and saving to output.

    Parameters
    ----------
    input_path : str
        Path to the input PDF file.
    output_path : str
        Path to save the flattened PDF file.

    Returns
    -------
    str
        Path to the saved flattened PDF file.
    """
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
    os.replace(resource_path("temp.pdf"), output_path)
    print(f"Flattened Business App saved to: {output_path}")

    return output_path

# def flatten_pdf_preserving_fields(input_path, output_path, font="lucida-console"):
#     """Flatten a PDF file while preserving form field data and fonts.

#     Parameters
#     ----------
#     input_path : str
#         Path to the input PDF file.
#     output_path : str
#         Path to save the flattened PDF file.
#     font : str, optional
#         Font name to use for form fields (default: "lucida-console").
#     """
#     pdfmetrics.registerFont(TTFont("lucida-console", resource_path("data/fonts/LUCON.TTF")))

#     # Load PDF and read form values
#     template_pdf = PdfReader(input_path)
#     overlays = []

#     for page in template_pdf.pages:
#         packet = io.BytesIO()
#         can = canvas.Canvas(packet, pagesize=letter)

#         if page.Annots:
#             for annot in page.Annots:
#                 if annot.Subtype == '/Widget' and annot.T and annot.V:
#                     # da = str(annot.get('/DA'))
#                     # size = da.split("Tf")[0].split()[-1]
#                     value = annot.V.to_unicode() if hasattr(annot.V, 'to_unicode') else str(annot.V)
#                     # print(f"{value}: {size}")
#                     rect = annot.Rect
#                     x, y = float(rect[0]), float(rect[1])
#                     height = float(rect[3]) - float(rect[1])
#                     width = float(rect[2]) - float(rect[0])
#                     # length = len(value)
#                     # font_size = min(0.8 * height, width/(1.8 * length))

#                     unit_width = pdfmetrics.stringWidth(value, font, 1)
#                     size_fit_width = width / unit_width
#                     size_fit_height = 0.8 * height
#                     font_size = min(size_fit_width, size_fit_height)

#                     can.setFont(font, font_size)
#                     can.drawString(x, y+2, value)

#         can.save()
#         packet.seek(0)
#         overlay_pdf = PdfReader(packet)
#         overlays.append(overlay_pdf.pages[0]) 

#     # Merge text overlays into the original pages
#     for i, page in enumerate(template_pdf.pages):
#         PageMerge(page).add(overlays[i]).render()
#         page.Annots = []  # remove interactive fields

#     PdfWriter().write(output_path, template_pdf)

# def flatten_pdf_preserving_fields(input_path, output_path, font="lucida-console"):
#     """Flatten a PDF file while preserving form field values."""
#     pdfmetrics.registerFont(TTFont("lucida-console", resource_path("data/fonts/LUCON.TTF")))

#     template_pdf = PdfReader(input_path)

#     for page in template_pdf.pages:
#         # --- Use the actual page size ---
#         mb = page.MediaBox
#         page_width = float(mb[2]) - float(mb[0])
#         page_height = float(mb[3]) - float(mb[1])

#         packet = io.BytesIO()
#         can = canvas.Canvas(packet, pagesize=(page_width, page_height))

#         if getattr(page, "Annots", None):
#             for annot in page.Annots:
#                 try:
#                     if annot.Subtype == "/Widget" and annot.T and annot.V:
#                         value = annot.V.to_unicode() if hasattr(annot.V, "to_unicode") else str(annot.V)
#                         rect = annot.Rect
#                         x, y = float(rect[0]), float(rect[1])
#                         height = float(rect[3]) - float(rect[1])
#                         width = float(rect[2]) - float(rect[0])

#                         if not value.strip():
#                             continue

#                         unit_width = pdfmetrics.stringWidth(value, font, 1)
#                         if unit_width <= 0:
#                             continue

#                         size_fit_width = width / unit_width
#                         size_fit_height = 0.8 * height
#                         font_size = max(1, min(size_fit_width, size_fit_height))

#                         can.setFont(font, font_size)
#                         can.drawString(x, y + 2, value)
#                 except Exception:
#                     # Skip any weird annotation safely
#                     continue

#         can.save()
#         packet.seek(0)

#         overlay_pdf = PdfReader(packet)

#         # --- Guard against empty overlay ---
#         if overlay_pdf.pages:
#             PageMerge(page).add(overlay_pdf.pages[0]).render()

#         # Remove fields after drawing values
#         page.Annots = []

#     PdfWriter().write(output_path, template_pdf)

def flatten_pdf_preserving_fields(input_path, output_path, font="lucida-console"):
    pdfmetrics.registerFont(TTFont("lucida-console", resource_path("data/fonts/LUCON.TTF")))

    template_pdf = PdfReader(input_path)
    overlays = []

    for page in template_pdf.pages:
        # Use actual page size
        media = page.MediaBox
        page_width = float(media[2]) - float(media[0])
        page_height = float(media[3]) - float(media[1])

        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(page_width, page_height))

        if page.Annots:
            for annot in page.Annots:
                if annot.Subtype != "/Widget":
                    continue

                field_name, value = _get_field_name_and_value(annot)
                if not value:
                    continue

                rect = annot.Rect
                x, y = float(rect[0]), float(rect[1])
                height = float(rect[3]) - float(rect[1])
                width = float(rect[2]) - float(rect[0])

                # Avoid divide-by-zero
                unit_width = pdfmetrics.stringWidth(value, font, 1)
                size_fit_width = width / unit_width
                size_fit_height = 0.8 * height
                font_size = min(size_fit_width, size_fit_height)

                can.setFont(font, font_size)
                can.drawString(x + 2, y + 2, value)

        can.showPage()
        can.save()

        overlay_pdf = PdfReader(fdata=packet.getvalue())
        if not overlay_pdf.pages:
            raise RuntimeError("Overlay PDF has no pages; ReportLab overlay failed.")
        overlays.append(overlay_pdf.pages[0])

    for i, page in enumerate(template_pdf.pages):
        PageMerge(page).add(overlays[i]).render()
        page.Annots = []

    PdfWriter().write(output_path, template_pdf)

def _get_field_name_and_value(annot):
    """Return (field_name, value_str) for a widget annot, checking /Parent."""
    # Field name might be on widget or parent
    name_obj = annot.get("/T")
    parent = annot.get("/Parent")
    if not name_obj and parent:
        name_obj = parent.get("/T")

    field_name = None
    if name_obj:
        field_name = str(name_obj)[1:-1].strip()  # "(Name)" -> "Name"

    # Value might be on widget or parent
    v_obj = annot.get("/V")
    if (v_obj is None or str(v_obj).strip() == "") and parent:
        v_obj = parent.get("/V")

    if v_obj is None:
        return field_name, None

    value = v_obj.to_unicode() if hasattr(v_obj, "to_unicode") else str(v_obj)
    return field_name, value
