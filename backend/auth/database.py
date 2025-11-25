"""
Configuración de base de datos PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# 🔥 Base de datos PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:68867805@localhost:5432/redes_sociales_db"
)

# Crear engine
engine = create_engine(DATABASE_URL)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear todas las tablas
def init_db():
    """Inicializa la base de datos"""
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos PostgreSQL inicializada")

# Dependency para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()