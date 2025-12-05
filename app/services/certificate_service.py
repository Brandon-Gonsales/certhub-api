# app/services/certificate_service.py

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw, ImageFont
import requests
import io
import cloudinary
import cloudinary.uploader
from datetime import datetime

from app.models.campaign_model import Campaign
from app.models.typography_model import Typography

async def generate_certificate_for_code(unique_code: str) -> StreamingResponse:
    """
    Servicio principal para generar un certificado a partir de un código único.
    Devuelve el certificado como archivo para descarga directa.
    """
    # 1. Busca la campaña que contiene al destinatario con este código.
    campaign = await Campaign.find_one({"recipients.unique_code": unique_code})
    
    if not campaign:
        raise HTTPException(status_code=404, detail="Código de certificado no válido.")

    # 2. Encuentra al destinatario específico dentro de la lista de la campaña.
    recipient = next((r for r in campaign.recipients if r.unique_code == unique_code), None)
    if not recipient:
        raise HTTPException(status_code=404, detail="Código de certificado no válido.")

    # 3. Reúne todos los ingredientes necesarios
    student_name = recipient.name
    template_url = campaign.template_image_url
    config = campaign.config

    if not template_url:
        raise HTTPException(status_code=500, detail="La campaña no tiene una plantilla de imagen configurada.")
    
    if not config:
        raise HTTPException(status_code=500, detail="La campaña no tiene configuración.")
        
    typography = await Typography.get(config.typography_id)
    if not typography:
        raise HTTPException(status_code=500, detail="La fuente configurada para esta campaña no fue encontrada.")
    font_url = typography.font_file_url

    # 4. Proceso de Generación de Imagen en Memoria
    try:
        # Descarga la plantilla y la fuente
        template_response = requests.get(template_url)
        template_response.raise_for_status()
        font_response = requests.get(font_url)
        font_response.raise_for_status()

        # Abre los archivos desde la memoria
        template_image = Image.open(io.BytesIO(template_response.content))
        font_bytes = io.BytesIO(font_response.content)
        
        # Prepara para dibujar
        draw = ImageDraw.Draw(template_image)
        
        # Dibuja el nombre del estudiante usando la configuración
        name_font = ImageFont.truetype(font_bytes, config.name_font_size)
        draw.text(
            (config.name_pos_x, config.name_pos_y),
            student_name,
            font=name_font,
            fill=config.name_color  # Usa el color de la configuración
        )
        
        # Dibuja el código único si está configurado
        if config.code_pos_x is not None and config.code_pos_y is not None:
            # Usa el tamaño y color de fuente configurados para el código
            code_font_size = config.code_font_size if config.code_font_size else 30
            code_color = config.code_color if config.code_color else "#000000"
            
            # Necesitamos recargar el font_bytes porque truetype lo consume
            font_bytes.seek(0)
            code_font = ImageFont.truetype(font_bytes, code_font_size)
            
            draw.text(
                (config.code_pos_x, config.code_pos_y),
                unique_code,
                font=code_font,
                fill=code_color
            )
        
        # Guarda la imagen final en un buffer de memoria, en formato PNG
        final_image_buffer = io.BytesIO()
        template_image.save(final_image_buffer, format="PNG")
        final_image_buffer.seek(0)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la generación de la imagen: {e}")

    # 5. Sube el certificado generado a Cloudinary (opcional, para respaldo)
    try:
        # Necesitamos hacer una copia del buffer porque upload lo consume
        buffer_copy = io.BytesIO(final_image_buffer.getvalue())
        upload_result = cloudinary.uploader.upload(
            buffer_copy, 
            folder=f"certhub-api/generated_certificates/{campaign.id}"
        )
        certificate_url = upload_result.get("secure_url")
        
        # Actualiza el documento del destinatario con la URL y fecha
        recipient.certificate_url = certificate_url
        recipient.claimed_at = datetime.utcnow()
        await campaign.save()
    except Exception as e:
        # Si falla la subida a Cloudinary, continuamos igual
        print(f"Error al subir a Cloudinary: {e}")

    # 6. Devuelve el certificado como archivo para descarga directa
    final_image_buffer.seek(0)
    
    # Nombre del archivo para descarga
    filename = f"certificado_{student_name.replace(' ', '_')}_{unique_code}.png"
    
    return StreamingResponse(
        final_image_buffer,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )