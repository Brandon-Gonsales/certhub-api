# app/services/email_service.py

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import asyncio

from app.core.config import settings
from app.models.campaign_model import Campaign

async def send_emails_in_background(campaign: Campaign):
    """
    Función que se ejecuta en segundo plano para enviar los correos usando SendGrid.
    """
    print(f"--- INICIANDO ENVÍO DE CORREOS PARA CAMPAÑA: {campaign.name} --- y el API KEY ES: {settings.SENDGRID_API_KEY}")
    
    # URL a la que el estudiante irá para reclamar su certificado
    claim_url = f"{settings.FRONTEND_URL}/claim-certificate"

    # Plantilla fija que se añade al final de cada correo
    EMAIL_FIXED_TEMPLATE = f"""
    <br><br>
    <hr>
    <p>Hola <strong>{{name}}</strong>,</p>
    <p>Tu código de acceso único es: <strong>{{unique_code}}</strong></p>
    <p>Puedes usarlo en la siguiente dirección para obtener tu certificado:</p>
    <p><a href="{claim_url}">{claim_url}</a></p>
    """

    for recipient in campaign.recipients:
        # Combinamos el cuerpo del correo de la campaña con nuestra plantilla
        html_body = campaign.email.body.replace('\n', '<br>') + EMAIL_FIXED_TEMPLATE.format(
            name=recipient.name,
            unique_code=recipient.unique_code
        )

        message = Mail(
            from_email='datahuba01@gmail.com',
            to_emails=recipient.email,
            subject=campaign.email.subject,
            html_content=html_body)

        try:
            # Inicializar cliente SendGrid
            # Es mejor inicializarlo fuera del loop si es posible, pero aquí está bien para manejo de errores individual
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            
            # Configuración opcional si es necesaria (ej. GDPR europeo)
            # sg.set_sendgrid_data_residency("global") 
            
            response = sg.send(message)
            
            print(f"Correo enviado a {recipient.email}. Status: {response.status_code}")
            
            # Actualizar estado del recipient (opcional, requeriría guardar en BD)
            recipient.email_status = "SENT"

        except Exception as e:
            print(f"Error al enviar correo a {recipient.email}: {e}")
            recipient.email_status = "FAILED"
        
        # Guardar el estado actualizado del recipient
        # Nota: Esto guarda todo el documento de la campaña por cada iteración.
        # Para optimizar, se podría guardar al final o por lotes, pero para seguridad se hace aquí.
        await campaign.save()

        await asyncio.sleep(0.2) # Pequeña pausa para evitar rate limits síncronos

    print(f"--- ENVÍO DE CORREOS FINALIZADO PARA CAMPAÑA: {campaign.name} ---")