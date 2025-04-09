import fitz  # PyMuPDF
import re

def redact_contact_info(input_path, output_path):
    doc = fitz.open(input_path)

    # Define patterns
    patterns = [
        r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",        # phone numbers
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",  # emails
        r"(?i)\bfax[: ]*"                            # case-insensitive "fax"
    ]

    compiled_patterns = [re.compile(p) for p in patterns]

    for page in doc:
        words = page.get_text("words")  # [x0, y0, x1, y1, "word", block_no, line_no, word_no]
        for w in words:
            word = w[4]
            for pattern in compiled_patterns:
                if pattern.search(word):
                    rect = fitz.Rect(w[0], w[1], w[2], w[3])
                    page.add_redact_annot(rect)

        page.apply_redactions()

    doc.save(output_path)
    print(f"Saved Sub Application to: {output_path}")

