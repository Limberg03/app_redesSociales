# 1. Base Image
FROM python:3.13-slim

# 2. Instalar dependencias del sistema (apt-get)
# Instala portaudio, herramientas de compilación, y librerías de audio necesarias.
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    build-essential \
    libasound-dev \
    libffi-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Configuración de PATHs para compilación (PyAudio fix)
# Esto indica dónde está el archivo 'portaudio.h' y las librerías binarias.
ENV C_INCLUDE_PATH=/usr/include/portaudio
ENV LIBRARY_PATH=/usr/lib/x86_64-linux-gnu

# 4. Crear la carpeta de trabajo
WORKDIR /usr/src/app

# 5. Copiar código
# Asumimos que el backend está en una carpeta 'backend/'
COPY backend/ ./backend/

# 6. Instalar dependencias de Python
# 'PyAudio' debería compilarse sin problemas ahora.
RUN pip install --no-cache-dir -r backend/requirements.txt

# 7. Comando de inicio
# Usa el módulo 'backend.main' y el puerto Render.
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]