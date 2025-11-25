# app/api/campaign_api.py

from fastapi import APIRouter, Depends, status, Response, UploadFile, File, BackgroundTasks
from beanie import PydanticObjectId
from typing import List 

from app.schemas.campaign_schema import CampaignCreate, CampaignDisplay, CampaignUpdate
from app.services import campaign_service
from app.core.security import get_current_user
from app.models.user_model import User

router = APIRouter()

@router.post(
    "/",
    response_model=CampaignDisplay,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new campaign"
)
async def create_new_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para crear una nueva campaña.

    - **name**: Nombre de la campaña.
    - **config**: Configuración de coordenadas, fuente, etc.
    - **email**: Asunto y cuerpo del correo.

    Esta ruta está protegida. Debes enviar un token de autorización válido.
    """
    print("--- 0. Endpoint /campaigns ha sido llamado ---")
    result = await campaign_service.create_campaign(campaign_data, current_user)
    return result

@router.get(
    "/",
    response_model=List[CampaignDisplay],
    summary="Get all campaigns for the current user"
)
async def get_all_campaigns(current_user: User = Depends(get_current_user)):
    """
    Endpoint para listar todas las campañas del usuario autenticado.
    """
    return await campaign_service.get_campaigns_by_user(current_user)


@router.get(
    "/{campaign_id}",
    response_model=CampaignDisplay,
    summary="Get a specific campaign by its ID"
)
async def get_one_campaign(
    campaign_id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para obtener los detalles de una campaña específica.
    """
    return await campaign_service.get_campaign_by_id(campaign_id, current_user)

@router.patch(
    "/{campaign_id}",
    response_model=CampaignDisplay,
    summary="Update a campaign partially"
)
async def update_one_campaign(
    campaign_id: PydanticObjectId,
    update_data: CampaignUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para actualizar parcialmente una campaña.
    Puedes enviar solo los campos que deseas cambiar.
    """
    return await campaign_service.update_campaign(campaign_id, update_data, current_user)

@router.delete(
    "/{campaign_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a campaign"
)
async def delete_one_campaign(
    campaign_id: PydanticObjectId,
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para eliminar una campaña.
    """
    await campaign_service.delete_campaign(campaign_id, current_user)
    
    # Devolvemos una respuesta sin contenido, que es el estándar para DELETE exitosos.
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post(
    "/{campaign_id}/upload-template",
    response_model=CampaignDisplay,
    summary="Upload a certificate template image"
)
async def upload_campaign_template(
    campaign_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...)
):
    """
    Endpoint para subir la imagen de plantilla de un certificado.
    
    Debes enviar el archivo como 'form-data'.
    """
    return await campaign_service.upload_template_image(
        campaign_id=campaign_id, file=file, current_user=current_user
    )

@router.post(
    "/{campaign_id}/upload-recipients",
    response_model=CampaignDisplay,
    summary="Upload and process the recipients Excel file"
)
async def upload_recipients(
    campaign_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...)
):
    """
    Endpoint para subir y procesar el archivo Excel con los destinatarios.
    
    El archivo debe contener las columnas 'nombre' y 'correo'.
    """
    return await campaign_service.process_recipients_file(
        campaign_id=campaign_id, file=file, current_user=current_user
    )

@router.post(
    "/{campaign_id}/activate",
    summary="Activate a campaign and start sending emails"
)
async def activate_one_campaign(
    campaign_id: PydanticObjectId,
    background_tasks: BackgroundTasks, # <-- FastAPI inyecta el objeto aquí
    current_user: User = Depends(get_current_user)
):
    """
    Endpoint para activar una campaña.
    
    Esto cambiará el estado de la campaña a 'SENDING' y comenzará
    el proceso de envío de correos a todos los destinatarios.
    La respuesta es inmediata.
    """
    return await campaign_service.activate_campaign(campaign_id, background_tasks, current_user)