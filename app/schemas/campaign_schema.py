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
    typography_name: str # <-- CAMBIO: Pedimos el nombre, no el ID
    code_pos_x: Optional[int] = None
    code_pos_y: Optional[int] = None
# --- Esquema para la CREACIÓN de una Campaña (SIN id) ---
class CampaignCreate(BaseModel):
    """
    Esquema para los datos que el cliente debe enviar para crear una campaña.
    Es la configuración inicial.
    """
    name: str
    config: ConfigCreate # <-- Usamos el nuevo esquema de config
    email: Campaign.EmailSettings

# --- Esquema para MOSTRAR una Campaña (CON id) ---
class CampaignDisplay(BaseModel):
    """
    Esquema para los datos que la API devolverá al mostrar una campaña.
    """
    id: PydanticObjectId
    user_id: PydanticObjectId
    name: str
    status: str
    template_image_url: Optional[str] = None
    config: Campaign.ConfigSettings
    email: Campaign.EmailSettings
    recipients: List[Recipient] = []
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
    config: Optional[Campaign.ConfigSettings] = None
    email: Optional[Campaign.EmailSettings] = None