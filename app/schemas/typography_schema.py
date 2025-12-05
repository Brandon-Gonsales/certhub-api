# app/schemas/typography_schema.py

from pydantic import BaseModel
from beanie import PydanticObjectId
from typing import Optional

# --- Esquema para CREAR una Tipografía ---
class TypographyCreate(BaseModel):
    """
    Esquema para crear una nueva tipografía.
    Solo se requiere el nombre, el archivo se sube por separado.
    """
    name: str


# --- Esquema para MOSTRAR una Tipografía ---
class TypographyDisplay(BaseModel):
    """
    Esquema para mostrar una tipografía.
    """
    id: PydanticObjectId
    name: str
    font_file_url: str
    
    class Config:
        from_attributes = True


# --- Esquema para ACTUALIZAR una Tipografía ---
class TypographyUpdate(BaseModel):
    """
    Esquema para actualizar una tipografía.
    Todos los campos son opcionales.
    """
    name: Optional[str] = None
    font_file_url: Optional[str] = None
