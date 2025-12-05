# app/services/campaign_service.py
from fastapi import HTTPException, status, UploadFile, BackgroundTasks, Form
from beanie import PydanticObjectId
from typing import List, Optional
import cloudinary
import cloudinary.uploader

from app.models.campaign_model import Campaign,Recipient
from app.models.user_model import User
from app.models.typography_model import Typography 
from app.models.plan_model import Plan 
from app.schemas.campaign_schema import CampaignCreate, CampaignUpdate
from datetime import datetime
from app.core.config import settings
from app.services import email_service

import pandas as pd
import secrets
import io
import json

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

async def create_campaign(campaign_data: CampaignCreate, current_user: User) -> Campaign:
    """
    Servicio para crear una nueva campaña en la base de datos.
    """
    # --------------------------------------------------
    # 2Busca el plan del usuario
    user_plan = await Plan.get(current_user.plan_id)
    if not user_plan:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No se pudo encontrar el plan asociado a tu cuenta."
        )

    #Cuenta cuántas campañas activas tiene ya el usuario
    current_campaign_count = await Campaign.find(
        Campaign.user_id == current_user.id
    ).count()

    #Compara con el límite del plan
    if current_campaign_count >= user_plan.max_campaigns:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Has alcanzado el límite de {user_plan.max_campaigns} campañas para tu plan '{user_plan.name}'. "
                   f"Considera actualizar tu plan."
        )
    # --------------------------------------------------
    # 1. Busca una tipografía por defecto (la primera que encuentre)
    # En el futuro, esto podría ser configurable por el sistema
    typography = await Typography.find_one({})
    
    if not typography:
        # Si no hay ninguna tipografía en el sistema, no podemos crear la configuración por defecto
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No hay tipografías configuradas en el sistema. Contacte al administrador."
        )

    # 2. Construye el objeto de configuración por DEFECTO
    default_config = Campaign.ConfigSettings(
        name_pos_x=100, # Valores por defecto arbitrarios, ajustables luego
        name_pos_y=100,
        name_font_size=20,
        name_color="#000000",
        typography_id=typography.id,
        code_pos_x=100,
        code_pos_y=150,
        code_font_size=12,
        code_color="#000000"
    )

    # 3. Construye el objeto de email por DEFECTO
    default_email = Campaign.EmailSettings(
        subject="Tu Certificado",
        body="Hola, adjunto encontrarás tu certificado."
    )

    # 4. Crea la instancia del modelo Campaign
    campaign = Campaign(
        user_id=current_user.id,
        name=campaign_data.name,
        config=default_config,
        email=default_email
    )

    # 5. Guarda la nueva campaña en la base de datos
    await campaign.create()
    
    return campaign

async def get_campaigns_by_user(current_user: User) -> List[Campaign]:
    """
    Servicio para obtener todas las campañas de un usuario específico.
    """
    return await Campaign.find(Campaign.user_id == current_user.id).to_list()


async def get_campaign_by_id(campaign_id: PydanticObjectId, current_user: User) -> Campaign:
    """
    Servicio para obtener una campaña específica por su ID.
    Verifica que la campaña pertenezca al usuario actual.
    """
    campaign = await Campaign.get(campaign_id)

    # Verificación de seguridad:
    # 1. ¿Existe la campaña?
    # 2. ¿Pertenece al usuario que la está pidiendo?
    if not campaign or campaign.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaña no encontrada."
        )
    
    return campaign

async def update_campaign(
    campaign_id: PydanticObjectId,
    update_data: CampaignUpdate,
    current_user: User
) -> Campaign:
    """
    Servicio para actualizar una campaña.
    """
    # 1. Reutilizamos nuestra función para obtener la campaña y verificar la propiedad
    campaign = await get_campaign_by_id(campaign_id, current_user)

    # 2. Convertimos el esquema de Pydantic a un diccionario, excluyendo los campos no establecidos
    update_dict = update_data.model_dump(exclude_unset=True)

    # 3. Iteramos sobre los datos a actualizar y los aplicamos al modelo
    for key, value in update_dict.items():
        setattr(campaign, key, value)
    
    # 4. Actualizamos la fecha de modificación
    campaign.updated_at = datetime.utcnow()

    # 5. Guardamos los cambios en la base de datos
    await campaign.save()
    
    return campaign

async def delete_campaign(campaign_id: PydanticObjectId, current_user: User):
    """
    Servicio para eliminar una campaña.
    """
    # 1. Reutilizamos nuestra función para obtener la campaña y verificar la propiedad.
    # Si la campaña no existe o no pertenece al usuario, esto lanzará un error 404.
    campaign = await get_campaign_by_id(campaign_id, current_user)

    # 2. Si la verificación es exitosa, eliminamos el documento.
    await campaign.delete()
    
    # No es necesario devolver nada, el éxito se comunica con el código de estado HTTP.
    return

async def upload_template_image(
    campaign_id: PydanticObjectId,
    file: UploadFile,
    current_user: User
) -> Campaign:
    """
    Servicio para subir una imagen de plantilla, guardarla en Cloudinary
    y actualizar la campaña correspondiente.
    """
    # Reutilizamos nuestra función para obtener la campaña y verificar la propiedad
    campaign = await get_campaign_by_id(campaign_id, current_user)

    # Sube el archivo a Cloudinary
    # Usamos una carpeta para mantener los templates organizados
    upload_result = cloudinary.uploader.upload(
        file.file, folder="certificate_templates"
    )

    # Obtenemos la URL segura del resultado
    secure_url = upload_result.get("secure_url")
    if not secure_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo subir la imagen a Cloudinary."
        )
    
    # Actualizamos el campo en nuestro documento de campaña
    campaign.template_image_url = secure_url
    await campaign.save()

    return campaign


async def upload_template_and_update_config(
    campaign_id: PydanticObjectId,
    file: UploadFile,
    config_json: str,
    current_user: User
) -> Campaign:
    """
    Servicio para subir una imagen de plantilla Y actualizar la configuración
    de la campaña en una sola operación.
    """
    # 1. Obtener la campaña y verificar la propiedad
    campaign = await get_campaign_by_id(campaign_id, current_user)

    # 2. Parsear la configuración desde JSON
    try:
        config_dict = json.loads(config_json)
        
        # Verificar si viene typography_name en lugar de typography_id
        if 'typography_name' in config_dict:
            typography_name = config_dict.pop('typography_name')
            
            # Buscar la tipografía por nombre
            typography = await Typography.find_one(Typography.name == typography_name)
            if not typography:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"La tipografía '{typography_name}' no fue encontrada."
                )
            
            # Reemplazar el nombre con el ID
            config_dict['typography_id'] = typography.id
        
        # Crear el objeto ConfigSettings con el ID de la tipografía
        config = Campaign.ConfigSettings(**config_dict)
    except HTTPException:
        raise  # Re-lanzar excepciones HTTP
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error al procesar la configuración: {str(e)}"
        )

    # 3. Subir el archivo a Cloudinary
    upload_result = cloudinary.uploader.upload(
        file.file, folder="certificate_templates"
    )

    # 4. Obtener la URL segura del resultado
    secure_url = upload_result.get("secure_url")
    if not secure_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo subir la imagen a Cloudinary."
        )
    
    # 5. Actualizar tanto la URL de la imagen como la configuración
    campaign.template_image_url = secure_url
    campaign.config = config
    campaign.updated_at = datetime.utcnow()
    await campaign.save()

    return campaign


async def process_recipients_file(
    campaign_id: PydanticObjectId,
    file: UploadFile,
    current_user: User
) -> Campaign:
    """
    Servicio para subir y procesar el archivo de destinatarios (Excel).
    """
    # 1. Obtiene la campaña y verifica la propiedad del usuario
    campaign = await get_campaign_by_id(campaign_id, current_user)

    # 2. Lee el archivo Excel usando pandas
    try:
        # Usamos un buffer de BytesIO para que pandas pueda leer el archivo en memoria
        contents = await file.read()
        buffer = io.BytesIO(contents)
        df = pd.read_excel(buffer)
        
        # Normaliza los nombres de las columnas a minúsculas y sin espacios (¡buena práctica de tu código!)
        df.columns = [str(col).strip().lower() for col in df.columns]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No se pudo procesar el archivo. Asegúrate de que es un Excel válido. Error: {e}"
        )

    # 3. Valida que las columnas 'nombre' y 'correo' existan
    required_columns = {'nombre', 'correo'}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo Excel debe contener las columnas 'nombre' y 'correo'."
        )

    # 4. Verifica que el número de destinatarios no exceda el límite del plan
    user_plan = await Plan.get(current_user.plan_id)
    if not user_plan:
        raise HTTPException(status_code=403, detail="Plan de usuario no encontrado.")
    
    if len(df) > user_plan.max_recipients_per_campaign:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"El número de destinatarios ({len(df)}) excede el límite de tu plan ({user_plan.max_recipients_per_campaign})."
        )
    
    # 5. Procesa cada fila para crear la lista de objetos Recipient
    recipients_list: List[Recipient] = []
    for index, row in df.iterrows():
        name = row.get('nombre')
        email = row.get('correo')

        # Si falta nombre o email en una fila, la ignoramos para evitar errores
        if pd.isna(name) or pd.isna(email) or name.strip() == "" or email.strip() == "":
            continue

        # Genera un código único de 8 caracteres alfanuméricos en mayúsculas
        unique_code = secrets.token_hex(4).upper()

        recipients_list.append(
            Recipient(name=str(name), email=str(email), unique_code=unique_code)
        )
    
    # 6. Sube el archivo original a Cloudinary para tener un respaldo
    upload_result = cloudinary.uploader.upload(
        contents,
        folder="recipient_files",
        resource_type="raw" # Importante para archivos no-media como Excel
    )
    
    # 7. Actualiza el documento de la campaña con la nueva lista y la URL del archivo
    campaign.recipients = recipients_list
    campaign.recipients_file_url = upload_result.get("secure_url")
    campaign.updated_at = datetime.utcnow() # Actualiza la fecha de modificación
    await campaign.save()

    return campaign

async def activate_campaign(campaign_id: PydanticObjectId, background_tasks: BackgroundTasks, current_user: User):
    """
    Servicio para activar una campaña y comenzar el envío de correos en segundo plano.
    """
    campaign = await get_campaign_by_id(campaign_id, current_user)

    # Validaciones
    if not campaign.template_image_url:
        raise HTTPException(status_code=400, detail="La campaña no tiene una plantilla de certificado subida.")
    if not campaign.recipients:
        raise HTTPException(status_code=400, detail="La campaña no tiene destinatarios. Sube el archivo Excel primero.")
    
    # Actualiza el estado de la campaña
    campaign.status = "SENDING"
    await campaign.save()

    # Añade la tarea de envío de correos para que se ejecute en segundo plano
    background_tasks.add_task(email_service.send_emails_in_background, campaign)

    return {"message": "La campaña ha sido activada. El envío de correos ha comenzado en segundo plano."}