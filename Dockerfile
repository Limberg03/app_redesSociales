# 1. Base Image: Usar la imagen de Python completa (más estable)
FROM python:3.13

# 2. Instalar dependencias del sistema (apt-get)
# Solo necesitamos ffmpeg y las herramientas básicas de compilación.
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Crear la carpeta de trabajo
WORKDIR /usr/src/app

# 4. Copiar código
# Copia la carpeta 'backend' completa al contenedor
COPY backend/ ./backend/

# 5. Instalar dependencias de Python (sin PyAudio)
RUN pip install --no-cache-dir -r backend/requirements.txt

# 6. Comando de inicio
# Usa el módulo 'backend.main' y el puerto Render (mapeado a 10000)
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10000"]