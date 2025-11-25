# app/api/dependencies.py

from fastapi.security import OAuth2PasswordBearer

# Esta línea crea un objeto que FastAPI usará para buscar el token
# en la cabecera 'Authorization' de la petición.
# El 'tokenUrl' le dice a la documentación interactiva (/docs)
# qué endpoint debe usar para obtener el token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")