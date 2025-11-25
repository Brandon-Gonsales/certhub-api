# app/models/campaign_model.py

from beanie import Document, PydanticObjectId, Indexed
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# --- Sub-documento para un Destinatario (Embebido) ---
class Recipient(BaseModel):
    """
    Representa a un único destinatario dentro de una campaña.
    NO es una colección separada, vivirá dentro del array 'recipients' de una Campaña.
    """
    name: str
    email: str
    unique_code: Indexed(str, unique=True) # ¡Índice para búsquedas rápidas!
    email_status: str = Field(default="PENDING") # PENDING, SENT, FAILED
    certificate_url: Optional[str] = None
    claimed_at: Optional[datetime] = None


# --- Documento Principal de la Campaña ---
class Campaign(Document):
    """
    Modelo principal para una campaña de certificados.
    """
    user_id: PydanticObjectId
    name: str
    status: str = Field(default="DRAFT") # DRAFT, READY, SENDING, COMPLETED
    template_image_url: Optional[str] = None
    recipients_file_url: Optional[str] = None

    # Agrupamos la configuración en sub-documentos para mayor orden
    class ConfigSettings(BaseModel):
        name_pos_x: int
        name_pos_y: int
        name_font_size: int
        typography_id: PydanticObjectId
        code_pos_x: Optional[int] = None
        code_pos_y: Optional[int] = None

    class EmailSettings(BaseModel):
        subject: str
        body: str

    config: ConfigSettings
    email: EmailSettings

    # Array de documentos embebidos
    recipients: List[Recipient] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "campaigns"