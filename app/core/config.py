# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

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

    # Email settings - AÑADE ESTAS LÍNEAS
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool

    # Frontend URL - AÑADE ESTA LÍNEA
    FRONTEND_URL: str

settings = Settings()