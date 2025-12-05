# app/services/typography_service.py

from fastapi import HTTPException, status, UploadFile
from beanie import PydanticObjectId
from typing import List
import cloudinary
import cloudinary.uploader

from app.models.typography_model import Typography
from app.schemas.typography_schema import TypographyCreate, TypographyUpdate
from datetime import datetime
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)


async def create_typography(typography_data: TypographyCreate, file: UploadFile) -> Typography:
    """
    Servicio para crear una nueva tipografía y subir el archivo de fuente a Cloudinary.
    """
    # 1. Verificar que no exista una tipografía con el mismo nombre
    existing = await Typography.find_one(Typography.name == typography_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe una tipografía con el nombre '{typography_data.name}'."
        )
    
    # 2. Subir el archivo de fuente a Cloudinary
    # Estructura: certhub-api/typographies/nombre_archivo
    upload_result = cloudinary.uploader.upload(
        file.file,
        folder="certhub-api/typographies",
        resource_type="raw"  # Para archivos que no son imágenes
    )
    
    # 3. Obtener la URL segura del archivo
    font_url = upload_result.get("secure_url")
    if not font_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo subir el archivo de fuente a Cloudinary."
        )
    
    # 4. Crear la tipografía en la base de datos
    typography = Typography(
        name=typography_data.name,
        font_file_url=font_url
    )
    await typography.create()
    
    return typography


async def get_all_typographies() -> List[Typography]:
    """
    Servicio para obtener todas las tipografías.
    """
    return await Typography.find_all().to_list()


async def get_typography_by_id(typography_id: PydanticObjectId) -> Typography:
    """
    Servicio para obtener una tipografía por su ID.
    """
    typography = await Typography.get(typography_id)
    
    if not typography:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tipografía no encontrada."
        )
    
    return typography


async def update_typography(
    typography_id: PydanticObjectId,
    update_data: TypographyUpdate
) -> Typography:
    """
    Servicio para actualizar una tipografía.
    """
    typography = await get_typography_by_id(typography_id)
    
    # Convertir el esquema a diccionario, excluyendo campos no establecidos
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # Si se está actualizando el nombre, verificar que no exista otra tipografía con ese nombre
    if 'name' in update_dict:
        existing = await Typography.find_one(
            Typography.name == update_dict['name'],
            Typography.id != typography_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe otra tipografía con el nombre '{update_dict['name']}'."
            )
    
    # Aplicar las actualizaciones
    for key, value in update_dict.items():
        setattr(typography, key, value)
    
    await typography.save()
    
    return typography


async def update_typography_file(
    typography_id: PydanticObjectId,
    file: UploadFile
) -> Typography:
    """
    Servicio para actualizar solo el archivo de fuente de una tipografía.
    """
    typography = await get_typography_by_id(typography_id)
    
    # Subir el nuevo archivo a Cloudinary
    upload_result = cloudinary.uploader.upload(
        file.file,
        folder="certhub-api/typographies",
        resource_type="raw"
    )
    
    font_url = upload_result.get("secure_url")
    if not font_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo subir el archivo de fuente a Cloudinary."
        )
    
    # Actualizar la URL del archivo
    typography.font_file_url = font_url
    await typography.save()
    
    return typography


async def delete_typography(typography_id: PydanticObjectId):
    """
    Servicio para eliminar una tipografía.
    """
    typography = await get_typography_by_id(typography_id)
    
    # Eliminar el documento
    await typography.delete()
    
    return
