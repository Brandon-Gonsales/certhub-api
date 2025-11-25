# app/main.py

from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import init_db

# 1. Importa el router que acabamos de crear
from app.api import user_api, auth_api, campaign_api, certificate_api
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicación...")
    await init_db()
    yield
    print("Apagando aplicación...")


app = FastAPI(
    title="Certificate Generator API",
    description="API para crear y gestionar campañas de certificados.",
    version="0.1.0",
    lifespan=lifespan
)

# 2. Incluye el router en la aplicación, asignándole un prefijo y una etiqueta
app.include_router(user_api.router, prefix="/users", tags=["Users"])
app.include_router(auth_api.router, prefix="/auth", tags=["Authentication"])
app.include_router(campaign_api.router, prefix="/campaigns", tags=["Campaigns"])
app.include_router(certificate_api.router, prefix="/certificates", tags=["Certificates"])

@app.get("/", tags=["Health Check"])
def read_root():
    """Endpoint de comprobación de estado."""
    return {"status": "ok"}
