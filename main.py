from afs_parser import extract_afs_data
from fill_nrs import fill_nrs

def main():

    # Extract data from afs application
    afs_data = extract_afs_data("Business Application.pdf")
    # Fill NRS Application
    fill_nrs(afs_data, "./")

main()