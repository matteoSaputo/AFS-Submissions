# import fitz
# print(fitz.__doc__)
# print(fitz.__file__)
# print(fitz.__version__)
import fitz
doc = fitz.open("./data/data/NRS Funding Application - Cleaned.pdf")
page = doc[0]
