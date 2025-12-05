# app/schemas/campaign_schema.py

from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from datetime import datetime
from typing import List, Optional

# --- Importamos las clases de sub-documentos que ya definimos ---

from app.models.campaign_model import Campaign, Recipient

# --- Esquema ANIDADO para la configuración en la creación ---
class ConfigCreate(BaseModel):
    name_pos_x: int
    name_pos_y: int
    name_font_size: int
    name_color: str       
    code_pos_x: Optional[int] = None
    code_pos_y: Optional[int] = None
    code_font_size: Optional[int] = None
    code_color: Optional[str] = None 
    typography_id: PydanticObjectId
    
# --- Esquema para la CREACIÓN de una Campaña (SIN id) ---
class CampaignCreate(BaseModel):
    """
    Esquema para los datos que el cliente debe enviar para crear una campaña.
    Solo se requiere el nombre, el resto se configura por defecto.
    """
    name: str


# --- Esquema para actualizar configuración con nombre de tipografía ---
class ConfigUpdateWithTypographyName(BaseModel):
    """
    Esquema para actualizar la configuración usando el nombre de la tipografía
    en lugar del ID. Ideal para frontends que no manejan IDs.
    """
    name_pos_x: int
    name_pos_y: int
    name_font_size: int
    name_color: str = "#000000"
    code_pos_x: Optional[int] = None
    code_pos_y: Optional[int] = None
    code_font_size: Optional[int] = None
    code_color: Optional[str] = None 
    typography_name: str  # Nombre de la tipografía en lugar del ID


# --- Esquema para MOSTRAR una Campaña (CON id) ---
class CampaignDisplay(BaseModel):
    """
    Esquema para los datos que la API devolverá al mostrar una campaña.
    Se excluyen datos sensibles o masivos como la lista de destinatarios.
    """
    id: PydanticObjectId
    user_id: PydanticObjectId
    name: str
    status: str
    template_image_url: Optional[str] = None
    config: Campaign.ConfigSettings
    email: Campaign.EmailSettings
    # recipients: List[Recipient] = []  <-- Oculto por seguridad/rendimiento
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# --- Esquema para ACTUALIZAR una Campaña (PATCH) ---
class CampaignUpdate(BaseModel):
    """
    Esquema para actualizar una campaña existente.
    Todos los campos son opcionales.
    """
    name: Optional[str] = None
    status: Optional[str] = None
    template_image_url: Optional[str] = None
    recipients_file_url: Optional[str] = None
    config: Optional[Campaign.ConfigSettings] = None
    email: Optional[Campaign.EmailSettings] = None
    recipients: Optional[List[Recipient]] = None