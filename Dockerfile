# 1. Base Image
FROM python:3.13-slim

# 2. Instalar dependencias del sistema (apt-get)
# Instala portaudio19-dev y build-essential (que incluye gcc, necesario para compilar PyAudio)
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Configuración del contenedor
# Crea la carpeta de trabajo
WORKDIR /usr/src/app

# 4. Copiar código
# Copia la carpeta 'backend' completa al contenedor
COPY backend/ ./backend/
# Si tiene otros archivos de configuración necesarios en la raíz (ej. .env, etc), cópielos también
# COPY .env . 

# 5. Instalar dependencias de Python
# Asumimos que requirements.txt está en backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# 6. Comando de inicio
# Render mapea automáticamente el puerto interno (10000) a su puerto externo ($PORT)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]