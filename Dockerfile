# 1. Base Image: CAMBIO CRUCIAL -> Usar Python 3.11 (que sí tiene audioop)
FROM python:3.11

# 2. Instalar dependencias del sistema (apt-get)
# Mantenemos las librerías de audio y video que ya sabemos que funcionan
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libasound-dev \
    libsndfile1 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Crear la carpeta de trabajo
WORKDIR /usr/src/app

# 4. Copiar código
COPY backend/ ./backend/

# 5. Instalar dependencias de Python
RUN pip install --no-cache-dir -r backend/requirements.txt

# 6. Comando de inicio
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]