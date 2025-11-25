# app/models/typography_model.py

from beanie import Document

class Typography(Document):
    """
    Modelo para las tipografías.
    Cada documento representa una fuente disponible para los certificados.
    """
    name: str
    font_file_url: str

    class Settings:
        name = "typographies"