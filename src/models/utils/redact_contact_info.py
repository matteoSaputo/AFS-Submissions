import fitz  # PyMuPDF
import re
import os
from models.utils.resource_path import resource_path

def redact_contact_info(input_path, output_path):
    if os.path.exists(output_path):
        os.unlink(output_path)

    doc = fitz.open(input_path)

    # Define patterns
    patterns = [
        r"\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}\b", # very flexible phone numbers
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # emails
        # r"(?i)\bfax[: ]*"                            # case-insensitive "fax"
    ]

    compiled_patterns = [re.compile(p) for p in patterns]

    for page in doc:
        blocks = page.get_text("blocks")
        for block in blocks:
            if block[6] == 0:  # text block
                text = block[4]
                for pattern in compiled_patterns:
                    for match in pattern.finditer(text):
                        matched_text = match.group()
                        rects = page.search_for(matched_text)
                        for rect in rects:
                            page.add_redact_annot(rect)
        page.apply_redactions()

    temp = resource_path("test.pdf")
    doc.save(temp)
    os.rename(temp, output_path)
    print(f"Saved Sub Application to: {output_path}")

    return output_path