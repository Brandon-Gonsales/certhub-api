# app/services/email_service.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import asyncio

from app.core.config import settings
from app.models.campaign_model import Campaign

# Configuración de la conexión con los datos de nuestro .env
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_emails_in_background(campaign: Campaign):
    """
    Función que se ejecuta en segundo plano para enviar los correos.
    """
    print(f"--- INICIANDO ENVÍO DE CORREOS PARA CAMPAÑA: {campaign.name} ---")
    
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

    fm = FastMail(conf)
    for recipient in campaign.recipients:
        # Combinamos el cuerpo del correo de la campaña con nuestra plantilla
        html_body = campaign.email.body.replace('\n', '<br>') + EMAIL_FIXED_TEMPLATE.format(
            name=recipient.name,
            unique_code=recipient.unique_code
        )

        message = MessageSchema(
            subject=campaign.email.subject,
            recipients=[recipient.email],
            body=html_body,
            subtype="html"
        )
        
        try:
            await fm.send_message(message)
            print(f"Correo enviado exitosamente a {recipient.email}")
        except Exception as e:
            print(f"ERROR al enviar correo a {recipient.email}: {e}")
        
        await asyncio.sleep(1) # Pequeña pausa para no saturar el servidor de correos

    print(f"--- ENVÍO DE CORREOS FINALIZADO PARA CAMPAÑA: {campaign.name} ---")