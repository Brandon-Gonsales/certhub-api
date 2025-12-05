# app/api/campaign_api.py

from fastapi import APIRouter, Depends, status, Response, UploadFile, File, BackgroundTasks, Form
from beanie import PydanticObjectId
from typing import List

from app.schemas.campaign_schema import CampaignCreate, CampaignDisplay
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
    summary="Update campaign configuration, email, template and recipients"
)
async def update_campaign_config(
    campaign_id: PydanticObjectId,
    current_user: User = Depends(get_current_user),
    # Archivos
    template_image: UploadFile = File(...),
    recipients_file: UploadFile = File(None),
    # Configuración (todos requeridos)
    name_pos_x: int = Form(...),
    name_pos_y: int = Form(...),
    name_font_size: int = Form(...),
    name_color: str = Form(...),
    typography_id: str = Form(...),
    code_pos_x: int = Form(None),
    code_pos_y: int = Form(None),
    code_font_size: int = Form(None),
    code_color: str = Form(None),
    # Email (todos requeridos)
    email_subject: str = Form(...),
    email_body: str = Form(...)
):
    """
    Endpoint para actualizar configuración, email, plantilla y destinatarios de una campaña.
    
    Usa las funciones existentes del servicio para manejar cada parte.
    
    Campos requeridos (FormData):
    
    **Archivos:**
    - template_image: Imagen de plantilla del certificado (archivo, requerido)
    - recipients_file: Archivo Excel con destinatarios (archivo, opcional)
    
    **Configuración del certificado:**
    - name_pos_x: Posición X del nombre (int, requerido)
    - name_pos_y: Posición Y del nombre (int, requerido)
    - name_font_size: Tamaño de fuente del nombre (int, requerido)
    - name_color: Color del nombre (string, requerido)
    - typography_id: ID de la tipografía (string, requerido)
    - code_pos_x: Posición X del código (int, opcional)
    - code_pos_y: Posición Y del código (int, opcional)
    - code_font_size: Tamaño de fuente del código (int, opcional)
    - code_color: Color del código (string, opcional)
    
    **Email:**
    - email_subject: Asunto del email (string, requerido)
    - email_body: Cuerpo del email (string, requerido)
    """
    # 1. Subir plantilla y actualizar configuración usando función existente
    campaign = await campaign_service.upload_template_and_update_config_formdata(
        campaign_id=campaign_id,
        file=template_image,
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
    
    # 2. Actualizar email
    from app.models.campaign_model import Campaign
    email_settings = Campaign.EmailSettings(subject=email_subject, body=email_body)
    campaign.email = email_settings
    await campaign.save()
    
    # 3. Procesar archivo de destinatarios si se proporciona usando función existente
    if recipients_file is not None:
        campaign = await campaign_service.process_recipients_file(
            campaign_id=campaign_id,
            file=recipients_file,
            current_user=current_user
        )
    
    return campaign

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