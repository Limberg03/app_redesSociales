from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
from auth import auth_service
from auth.database import get_db
from auth.models import User

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Verifica que el usuario esté autenticado mediante el token
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    # Extraer token del header "Bearer TOKEN"
    try:
        token = authorization.replace("Bearer ", "")
    except:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = auth_service.verify_token(token, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    
    return user
