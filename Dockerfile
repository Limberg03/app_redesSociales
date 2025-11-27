# 1. Base Image: Usar la imagen base de Python completa (más robusta)
FROM python:3.13 

# 2. Instalar dependencias del sistema (apt-get)
# Instalamos todas las librerías necesarias para PyAudio, ffmpeg, y compilación.
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    build-essential \
    libasound-dev \
    libffi-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Crear la carpeta de trabajo
WORKDIR /usr/src/app

# 4. Copiar código
# Copia la carpeta 'backend' completa al contenedor
COPY backend/ ./backend/

# 5. Instalar dependencias de Python
# La compilación de PyAudio ahora debería encontrar los archivos.
RUN pip install --no-cache-dir -r backend/requirements.txt

# 6. Comando de inicio
# Usa el módulo 'backend.main' y el puerto Render (mapeado a 10000)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]