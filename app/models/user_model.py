# app/models/user_model.py

from beanie import Document, PydanticObjectId, Indexed
from pydantic import Field, EmailStr
from datetime import datetime

class User(Document):
    """
    Modelo para los usuarios.
    Cada instancia de esta clase representa un documento en la colección 'users'.
    """
    full_name: str
    email: Indexed(EmailStr, unique=True) # <-- ¡Importante!
    hashed_password: str
    is_active: bool = Field(default=True)
    plan_id: PydanticObjectId # <-- Referencia a un documento de Plan
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users" # Nombre de la colección en MongoDB