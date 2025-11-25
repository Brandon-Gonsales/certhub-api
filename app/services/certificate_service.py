# app/services/certificate_service.py

from fastapi import HTTPException, status
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import cloudinary
import cloudinary.uploader
from datetime import datetime

from app.models.campaign_model import Campaign
from app.models.typography_model import Typography

async def generate_certificate_for_code(unique_code: str) -> dict:
    """
    Servicio principal para generar un certificado a partir de un código único.
    """
    # 1. Busca la campaña que contiene al destinatario con este código.
    # Esta es una consulta muy eficiente gracias al índice que creamos.
    campaign = await Campaign.find_one({"recipients.unique_code": unique_code})
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Código de certificado no válido.")

    # 2. Encuentra al destinatario específico dentro de la lista de la campaña.
    recipient = next((r for r in campaign.recipients if r.unique_code == unique_code), None)
    if not recipient: # Doble chequeo, aunque la consulta anterior debería garantizarlo
        raise HTTPException(status_code=404, detail="Código de certificado no válido.")

    # 3. Si el certificado ya fue generado, devuelve la URL existente para ahorrar recursos.
    if recipient.certificate_url:
        return {"certificate_url": recipient.certificate_url}

    # 4. Reúne todos los ingredientes necesarios
    student_name = recipient.name
    template_url = campaign.template_image_url
    font_id = campaign.config.typography_id

    if not template_url:
        raise HTTPException(status_code=500, detail="La campaña no tiene una plantilla de imagen configurada.")
        
    typography = await Typography.get(font_id)
    if not typography:
        raise HTTPException(status_code=500, detail="La fuente configurada para esta campaña no fue encontrada.")
    font_url = typography.font_file_url

    # 5. Proceso de Generación de Imagen en Memoria
    try:
        # Descarga la plantilla y la fuente
        template_response = requests.get(template_url)
        template_response.raise_for_status() # Lanza un error si la descarga falla
        font_response = requests.get(font_url)
        font_response.raise_for_status()

        # Abre los archivos desde la memoria
        template_image = Image.open(io.BytesIO(template_response.content))
        font_bytes = io.BytesIO(font_response.content)
        
        # Prepara para dibujar
        draw = ImageDraw.Draw(template_image)
        font = ImageFont.truetype(font_bytes, campaign.config.name_font_size)
        
        # Dibuja el nombre del estudiante
        draw.text(
            (campaign.config.name_pos_x, campaign.config.name_pos_y),
            student_name,
            font=font,
            fill="black" # Puedes hacer esto configurable en el futuro
        )
        # Dibuja el código único (opcional)
        if campaign.config.code_pos_x is not None and campaign.config.code_pos_y is not None:
            # Usamos una fuente más pequeña por defecto para el código
            code_font = ImageFont.truetype(io.BytesIO(font_response.content), 30) 
            draw.text(
                (campaign.config.code_pos_x, campaign.config.code_pos_y),
                unique_code,
                font=code_font,
                fill="black"
            )
        
        # Guarda la imagen final en un buffer de memoria, en formato PNG
        final_image_buffer = io.BytesIO()
        template_image.save(final_image_buffer, format="PNG")
        final_image_buffer.seek(0)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la generación de la imagen: {e}")

    # 6. Sube el certificado generado a Cloudinary
    upload_result = cloudinary.uploader.upload(
        final_image_buffer, folder="generated_certificates"
    )
    certificate_url = upload_result.get("secure_url")

    # 7. Actualiza el documento del destinatario en la base de datos con la nueva URL
    recipient.certificate_url = certificate_url
    recipient.claimed_at = datetime.utcnow()
    await campaign.save()

    return {"certificate_url": certificate_url}