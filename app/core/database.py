# app/core/database.py

import motor.motor_asyncio
from beanie import init_beanie

# 1. Importa los modelos que acabamos de crear
from app.models.user_model import User
from app.models.plan_model import Plan
from app.models.typography_model import Typography
from app.models.campaign_model import Campaign
from .config import settings

async def init_db():
    """
    Initializes the database connection and Beanie ODM.
    """
    client = motor.motor_asyncio.AsyncIOMotorClient(
        settings.DATABASE_URL
    )

    # 2. Añade los modelos a la lista `document_models`
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            User,
            Plan,
            Typography,
            Campaign,
        ]
    )
    print("Database connection successful and Beanie initialized.")