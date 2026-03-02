from models.main_model import MainModel

class EmailModel(MainModel):
    """Model for email-related features, extends MainModel."""

    def __init__(self):
        """Initialize the EmailModel."""
        super().__init__()