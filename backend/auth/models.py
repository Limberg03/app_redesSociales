"""
Modelos de base de datos para el sistema de autenticación
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import hashlib

Base = declarative_base()


class User(Base):
    """Modelo de Usuario"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def verify_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return self.hashed_password == hashed
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash de una contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"