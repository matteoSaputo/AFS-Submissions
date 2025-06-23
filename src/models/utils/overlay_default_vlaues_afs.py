import fitz
from models.utils.resource_path import resource_path

def overlay_default_values_afs(input_path, output_path, missing_data):
    if not missing_data:
        return None

    doc = fitz.open(input_path)
    page = doc[0]  # Assuming all data is on page 1

    # Define positions
    field_coords = {
        "S S N": (65, 280),  
        "Ssn": (65, 280),                                
        "Date Of Birth": (305, 280),
        "Business Start Date": (325, 180)
    }

    # Load the custom Lucida Console font
    font_path = resource_path("data/fonts/LUCON.TTF")

    # Font settings
    font_size = 9
    font_color = (0, 0, 0)  # Black

    for field, value in missing_data.items():
        if field in field_coords and value.strip():
            x, y = field_coords[field]
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

    doc.save(output_path)
    return output_path