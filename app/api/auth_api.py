# app/api/auth_api.py
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user_schema import Token
from app.services import auth_service

router = APIRouter()

@router.post("/login", response_model=Token, summary="User Login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Endpoint para iniciar sesión. Devuelve un token de acceso.
    """
    try:
        return await auth_service.login_for_access_token(form_data)
    except HTTPException as e:
        raise e