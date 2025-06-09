import fitz  # PyMuPDF
import os

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
