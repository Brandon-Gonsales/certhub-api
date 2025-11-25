# app/models/plan_model.py

from beanie import Document
from pydantic import Field
from datetime import datetime

class Plan(Document):
    """
    Modelo para los planes de suscripción.
    Cada instancia de esta clase representa un documento en la colección 'plans'.
    """
    name: str
    max_campaigns: int
    max_recipients_per_campaign: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "plans" # Nombre de la colección en MongoDB