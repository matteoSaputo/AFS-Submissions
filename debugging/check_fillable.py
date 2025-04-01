from PyPDF2 import PdfReader
reader = PdfReader("NRS Funding Application.pdf")
fields = reader.get_fields()
for f in fields:
    print(f)