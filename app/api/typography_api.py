# app/api/typography_api.py

from fastapi import APIRouter, Depends, status, Response, UploadFile, File
from beanie import PydanticObjectId
from typing import List

from app.schemas.typography_schema import TypographyCreate, TypographyDisplay, TypographyUpdate
from app.services import typography_service
from app.core.security import get_current_user
from app.models.user_model import User

router = APIRouter()


@router.post(
    "/",
    response_model=TypographyDisplay,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new typography with font file"
)
async def create_new_typography(
    name: str = File(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para crear una nueva tipografía y subir su archivo de fuente.
    
    Debes enviar:
    - name: Nombre de la tipografía (form-data)
    - file: Archivo de fuente (.ttf, .otf, .woff, etc.) (form-data)
    
    El archivo se subirá a Cloudinary en la carpeta: certhub-api/typographies
    
    Esta ruta está protegida. Debes enviar un token de autorización válido.
    """
    typography_data = TypographyCreate(name=name)
    return await typography_service.create_typography(typography_data, file)


@router.get(
    "/",
    response_model=List[TypographyDisplay],
    summary="Get all typographies"
)
async def get_all_typographies():
    """
    Endpoint para listar todas las tipografías disponibles.
    """
    return await typography_service.get_all_typographies()


@router.get(
    "/{typography_id}",
    response_model=TypographyDisplay,
    summary="Get a specific typography by ID"
)
async def get_one_typography(typography_id: PydanticObjectId):
    """
    Endpoint para obtener los detalles de una tipografía específica.
    """
    return await typography_service.get_typography_by_id(typography_id)


@router.patch(
    "/{typography_id}",
    response_model=TypographyDisplay,
    summary="Update a typography (name only)"
)
async def update_one_typography(
    typography_id: PydanticObjectId,
    update_data: TypographyUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para actualizar una tipografía (solo el nombre).
    
    Para actualizar el archivo de fuente, usa el endpoint PATCH /{typography_id}/upload-font
    """
    return await typography_service.update_typography(typography_id, update_data)


@router.patch(
    "/{typography_id}/upload-font",
    response_model=TypographyDisplay,
    summary="Update typography font file"
)
async def update_typography_font(
    typography_id: PydanticObjectId,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para actualizar solo el archivo de fuente de una tipografía.
    
    Debes enviar:
    - file: Nuevo archivo de fuente (form-data)
    
    El archivo se subirá a Cloudinary en la carpeta: certhub-api/typographies
    """
    return await typography_service.update_typography_file(typography_id, file)


@router.delete(
    "/{typography_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a typography"
)
async def delete_one_typography(
    typography_id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para eliminar una tipografía.
    """
    await typography_service.delete_typography(typography_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
