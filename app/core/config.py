# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database settings
    DATABASE_URL: str
    DATABASE_NAME: str

    # JWT settings - NUEVAS LÍNEAS
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Cloudinary settings - AÑADE ESTAS LÍNEAS
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    # Email settings
    MAIL_FROM: str
    SENDGRID_API_KEY: str

    # Frontend URL - AÑADE ESTA LÍNEA
    FRONTEND_URL: str

    @field_validator("SENDGRID_API_KEY")
    @classmethod
    def clean_api_key(cls, v):
        return v.strip() if v else v


settings = Settings()