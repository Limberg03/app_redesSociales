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