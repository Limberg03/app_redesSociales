"""
Servicio de autenticación
"""
from sqlalchemy.orm import Session
from .models import User
import secrets
from typing import Optional


# Almacenamiento simple de tokens en memoria (para producción usar Redis)
active_tokens = {}


def create_user(db: Session, username: str, email: str, password: str) -> User:
    """
    Crea un nuevo usuario en la base de datos
    """
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise ValueError("Usuario o email ya existe")
    
    # Crear nuevo usuario
    hashed_password = User.hash_password(password)
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Autentica un usuario
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not user.verify_password(password):
        return None
    
    if not user.is_active:
        return None
    
    return user


def create_access_token(user: User) -> str:
    """
    Crea un token de acceso para el usuario
    """
    token = secrets.token_urlsafe(32)
    active_tokens[token] = user.id
    return token


def verify_token(token: str, db: Session) -> Optional[User]:
    """
    Verifica si un token es válido y retorna el usuario
    """
    user_id = active_tokens.get(token)
    
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


def logout_user(token: str):
    """
    Elimina el token (logout)
    """
    if token in active_tokens:
        del active_tokens[token]
        return True
    return False