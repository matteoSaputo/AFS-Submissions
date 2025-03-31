import pdfplumber
import re
from afs_parser import extract_afs_data
import pdfrw

# Step 1: Extract data from the AFS Application
afs_data = extract_afs_data("Business Application.pdf")

for k in afs_data:
    print(f'{k}: {afs_data[k]}')