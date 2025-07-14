import fitz
from models.utils.resource_path import resource_path

FIELD_CORRDS = {
    "SSN": (65, 280),                                
    "Date Of Birth": (305, 280),
    "Business Start Date": (325, 180)
}


def normalize_key(key: str):
    return key.strip().replace(",", "").replace("\xa0", "").replace(" ", "").lower()

def overlay_default_values_afs(input_path, output_path, missing_data: dict):
    if not missing_data:
        return None

    doc = fitz.open(input_path)
    page = doc[0]  # Assuming all data is on page 1

    # Normalize field names 
    normalized_missing = {normalize_key(k): v for k, v in missing_data.items()}
    normalized_coords = {normalize_key(k): v for k, v in FIELD_CORRDS.items()}

    # Load the custom Lucida Console font
    font_path = resource_path("data/fonts/LUCON.TTF")

    # Font settings
    font_size = 9
    font_color = (0, 0, 0)  # Black

    for field, value in normalized_missing.items():
        if field in normalized_coords and value.strip():
            x, y = normalized_coords[field]
            # Use insert_textbox to allow font embedding
            rect = fitz.Rect(x, y, x + 200, y + 15)  # Adjust width/height as needed
            page.insert_textbox(
                rect,
                value,
                fontname="lucida-console",     
                fontfile=font_path,          
                fontsize=font_size,
                color=font_color,
                align=0  # left-align
            )
    print(missing_data)
    doc.save(output_path)
    return output_path