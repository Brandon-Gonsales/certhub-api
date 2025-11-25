# app/schemas/certificate_schema.py

from pydantic import BaseModel

class CertificateClaimRequest(BaseModel):
    unique_code: str

class CertificateClaimResponse(BaseModel):
    certificate_url: str