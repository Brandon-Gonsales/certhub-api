# app/schemas/campaign_schema.py

from pydantic import BaseModel, Field
from beanie import PydanticObjectId
from datetime import datetime
from typing import List, Optional

# --- Importamos las clases de sub-documentos que ya definimos ---

from app.models.campaign_model import Campaign, Recipient

# --- Esquema para la CREACIÓN de una Campaña (SIN id) ---
class CampaignCreate(BaseModel):
    """
    Esquema para los datos que el cliente debe enviar para crear una campaña.
    Solo se requiere el nombre, el resto se configura por defecto.
    """
    name: str


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

