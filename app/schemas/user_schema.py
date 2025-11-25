# app/schemas/user_schema.py

from pydantic import BaseModel, EmailStr, Field
from beanie import PydanticObjectId

# ====================================================================
# Esquema para la Creación de un Usuario (Input)
# ====================================================================
class UserCreate(BaseModel):
    """
    Esquema para los datos que el cliente debe enviar para crear un usuario.
    """
    full_name: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)

# ====================================================================
# Esquema para Mostrar un Usuario (Output)
# ====================================================================
class UserDisplay(BaseModel):
    """
    Esquema para los datos que la API devolverá al mostrar un usuario.
    Es la versión "segura" del modelo, sin la contraseña.
    """
    id: PydanticObjectId
    full_name: str
    email: EmailStr

    class Config:
        from_attributes = True # Permite crear el esquema desde un objeto de modelo

# ====================================================================
# Esquemas para Autenticación (Login)
# ====================================================================
class Token(BaseModel):
    """
    Esquema para la respuesta del token de autenticación.
    """
    access_token: str
    token_type: str