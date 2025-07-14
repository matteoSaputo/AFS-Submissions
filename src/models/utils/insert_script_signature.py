import fitz
import os

from models.utils.resource_path import resource_path

def insert_script_signature(pdf_path, output_path, owner_name, field_coords):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)

    rect = fitz.Rect(field_coords)
    font_path = resource_path("data/fonts/Allura-Regular.ttf")
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