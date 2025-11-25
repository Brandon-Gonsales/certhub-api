# app/api/user_api.py

from fastapi import APIRouter, status, HTTPException, Depends

from app.schemas.user_schema import UserCreate, UserDisplay
from app.services import user_service

from app.core.security import get_current_user
from app.models.user_model import User

router = APIRouter()

@router.post(
    "/register",
    response_model=UserDisplay,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register_user(user_data: UserCreate):
    """
    Endpoint para registrar un nuevo usuario.
    """
    try:
        new_user = await user_service.create_user(user_data)
        return new_user
    except HTTPException as e:
        # Re-lanzar las excepciones HTTP que vienen del servicio
        raise e
    except Exception as e:
        # Manejar errores inesperados del servidor
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}"
        )
@router.get(
    "/me",
    response_model=UserDisplay,
    summary="Get current user's information"
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Endpoint para obtener la información del usuario autenticado actualmente.
    """
    return current_user