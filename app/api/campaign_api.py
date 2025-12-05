# app/api/campaign_api.py

from fastapi import APIRouter, Depends, status, Response, UploadFile, File, BackgroundTasks, Form
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



@router.patch(
    "/{campaign_id}/upload-template-and-config",
    response_model=CampaignDisplay,
    summary="Upload template image and update config in one request"
)
async def upload_template_and_config(
    campaign_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    name_pos_x: int = Form(...),
    name_pos_y: int = Form(...),
    name_font_size: int = Form(...),
    name_color: str = Form("#000000"),
    typography_id: str = Form(...),
    code_pos_x: int = Form(None),
    code_pos_y: int = Form(None),
    code_font_size: int = Form(None),
    code_color: str = Form(None)
):
    """
    Endpoint para subir la imagen de plantilla Y actualizar la configuración
    de la campaña en una sola operación usando FormData.
    
    Debes enviar todos los campos como form-data:
    - file: La imagen de plantilla (archivo)
    - name_pos_x: Posición X del nombre (int)
    - name_pos_y: Posición Y del nombre (int)
    - name_font_size: Tamaño de fuente del nombre (int)
    - name_color: Color del nombre (string, ej: "#FFFFFF")
    - typography_id: ID de la tipografía (string)
    - code_pos_x: Posición X del código (int, opcional)
    - code_pos_y: Posición Y del código (int, opcional)
    - code_font_size: Tamaño de fuente del código (int, opcional)
    - code_color: Color del código (string, opcional)
    """
    return await campaign_service.upload_template_and_update_config_formdata(
        campaign_id=campaign_id,
        file=file,
        name_pos_x=name_pos_x,
        name_pos_y=name_pos_y,
        name_font_size=name_font_size,
        name_color=name_color,
        typography_id=typography_id,
        code_pos_x=code_pos_x,
        code_pos_y=code_pos_y,
        code_font_size=code_font_size,
        code_color=code_color,
        current_user=current_user
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