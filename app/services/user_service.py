# app/services/user_service.py

from passlib.context import CryptContext
from fastapi import HTTPException, status
from beanie import PydanticObjectId

from app.models.user_model import User
from app.models.plan_model import Plan
from app.schemas.user_schema import UserCreate

from app.core.security import get_password_hash 

async def get_default_plan() -> PydanticObjectId:
    """
    Busca el plan por defecto ("Gratuito") en la base de datos.
    """
    # ¡IMPORTANTE! Debes crear este plan en tu base de datos primero.
    default_plan = await Plan.find_one(Plan.name == "Gratuito")
    if not default_plan:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Plan 'Gratuito' no encontrado. Por favor, créelo en la base de datos."
        )
    return default_plan.id

async def create_user(user_data: UserCreate) -> User:
    """
    Servicio para crear un nuevo usuario en la base de datos.
    """
    # 1. Verificar si el email ya existe
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con este correo electrónico."
        )

    # 2. Hashear la contraseña
    hashed_password = get_password_hash(user_data.password)


    # 3. Obtener el ID del plan por defecto
    default_plan_id = await get_default_plan()

    # 4. Crear la instancia del modelo User con los datos validados
    user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hashed_password,
        plan_id=default_plan_id
    )

    # 5. Guardar el nuevo usuario en la base de datos
    await user.create()
    return user