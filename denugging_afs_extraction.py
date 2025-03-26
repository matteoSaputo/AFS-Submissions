import pdfplumber

def extract_full_text(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"
    return full_text

full_text = extract_full_text("AFS Application.pdf")
print(full_text[:1000])  # Print the first 1000 characters for inspection

import re

# Test extraction for "Business Legal Name"
match = re.search(r'\* Business Legal Name:\s*(.*)', full_text)
if match:
    print("Legal Name found:", match.group(1).strip())
else:
    print("Legal Name Not Found")
