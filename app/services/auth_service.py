# app/services/auth_service.py

from datetime import timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user_model import User
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.user_schema import Token

async def login_for_access_token(form_data: OAuth2PasswordRequestForm) -> Token:
    """
    Verifica las credenciales del usuario y devuelve un token JWT.
    """
    # 1. Busca al usuario por su email (en OAuth2, el 'username' es nuestro email)
    user = await User.find_one(User.email == form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verifica que la contraseña coincida
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Crea el token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")