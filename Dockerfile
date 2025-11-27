# 1. Base Image: Usar la imagen de Python completa (más estable)
FROM python:3.13

# 2. Instalar dependencias del sistema (apt-get)
# Instala ffmpeg, build-essential y las librerías de audio necesarias.
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

# 5. Instalar dependencias de Python (sin PyAudio, ya lo eliminó)
RUN pip install --no-cache-dir -r backend/requirements.txt

# 6. Comando de inicio (Corregido a la ruta de módulo)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]