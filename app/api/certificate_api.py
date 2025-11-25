# app/api/certificate_api.py

from fastapi import APIRouter

from app.schemas.certificate_schema import CertificateClaimRequest, CertificateClaimResponse
from app.services import certificate_service

router = APIRouter()

@router.post(
    "/claim",
    response_model=CertificateClaimResponse,
    summary="Claim and generate a certificate"
)
async def claim_certificate(request_data: CertificateClaimRequest):
    """
    Endpoint público para que un estudiante reclame su certificado.

    El estudiante envía su código único y, si es válido, la API
    genera el certificado y devuelve la URL para descargarlo.
    """
    return await certificate_service.generate_certificate_for_code(request_data.unique_code)