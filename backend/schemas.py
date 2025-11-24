from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Modelo para el JSON que recibimos en el request
class AdaptRequest(BaseModel):
    titulo: str
    contenido: str
    target_networks: List[str] 

class AdaptResponse(BaseModel):
    data: Dict[str, Any]



class TestPostRequest(BaseModel):
    text: str
    image_url: Optional[str] = None  # Ahora es opcional

class TestPostRequestLinkedIn(BaseModel):
    text: str


class MultiNetworkPostRequest(BaseModel):
    """
    Request para publicar en múltiples redes sociales simultáneamente
    
    Ejemplo:
    {
        "text": "La UAGRM anuncia nuevas inscripciones",
        "target_networks": ["facebook", "instagram", "linkedin", "tiktok"]
    }
    """
    text: str
    target_networks: List[str]    

class MultiNetworkPostResponse(BaseModel):
    """
    Respuesta con resultados de cada red social
    """
    validacion: Dict[str, Any]
    resultados: Dict[str, Dict[str, Any]]
    resumen: Dict[str, Any]    