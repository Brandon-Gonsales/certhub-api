# app/api/certificate_api.py

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.certificate_schema import CertificateClaimRequest
from app.services import certificate_service

router = APIRouter()

@router.post(
    "/claim",
    summary="Claim and download a certificate",
    response_class=StreamingResponse
)
async def claim_certificate(request_data: CertificateClaimRequest) -> StreamingResponse:
    """
    Endpoint público para que un estudiante reclame su certificado.

    El estudiante envía su código único y, si es válido, la API
    genera el certificado y lo devuelve como archivo PNG para descarga directa.
    
    El certificado también se guarda en Cloudinary como respaldo.
    """
    return await certificate_service.generate_certificate_for_code(request_data.unique_code)