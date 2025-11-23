# 🎬 Configuración para TikTok Video Generation

Este documento explica cómo configurar el sistema para generar videos de TikTok con IA.

## ❌ Problema Común: FFmpeg no encontrado

Si ves el error:
```
❌ Error combinando videos: [WinError 2] El sistema no puede encontrar el archivo especificado
```

Significa que **FFmpeg no está instalado** en tu sistema.

## ✅ Solución: Instalar FFmpeg

### Windows

1. **Descarga FFmpeg:**
   - Ve a: https://www.gyan.dev/ffmpeg/builds/
   - Descarga: `ffmpeg-release-essentials.zip` (versión más pequeña)
   - O descarga: `ffmpeg-release-full.zip` (versión completa)

2. **Extrae el archivo:**
   - Extrae el ZIP en una ubicación permanente (ej: `C:\ffmpeg`)

3. **Agrega FFmpeg al PATH:**
   - Abre "Variables de entorno" (busca en el menú inicio)
   - En "Variables del sistema", busca la variable `Path`
   - Haz clic en "Editar"
   - Haz clic en "Nuevo"
   - Agrega la ruta a la carpeta `bin` de FFmpeg (ej: `C:\ffmpeg\bin`)
   - Haz clic en "Aceptar" en todas las ventanas

4. **Verifica la instalación:**
   ```bash
   ffmpeg -version
   ```
   Si ves la versión de FFmpeg, ¡está instalado correctamente!

### macOS

```bash
brew install ffmpeg
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg
```

## 📦 Instalar dependencias Python

Asegúrate de instalar todas las dependencias necesarias:

```bash
cd backend
pip install -r requirements.txt
```

Esto instalará:
- `gTTS` - Para generar audio con Google Text-to-Speech
- `ffmpeg-python` - Wrapper de Python para FFmpeg
- Y todas las demás dependencias

## 🔑 Variables de Entorno Necesarias

Asegúrate de tener estas variables en tu archivo `.env`:

```env
# Para buscar videos de stock
PEXELS_API_KEY=tu_api_key_de_pexels

# Para publicar en TikTok
TIKTOK_ACCESS_TOKEN=tu_token_de_tiktok
```

### Obtener PEXELS_API_KEY:
1. Ve a https://www.pexels.com/api/
2. Crea una cuenta gratis
3. Obtén tu API key

## 🎯 Flujo de Generación de Video

1. **Validación:** El contenido es validado como académico
2. **Adaptación:** El texto es adaptado para TikTok (tono joven, viral)
3. **Keywords:** Se extraen 3 palabras clave del texto con IA
4. **Videos:** Se buscan videos de stock en Pexels para cada keyword
5. **Audio:** Se genera audio con Google TTS (gTTS)
6. **Combinación:** FFmpeg combina los videos y el audio
7. **Publicación:** El video se sube a TikTok (modo privado por defecto)

## 🧪 Probar el Sistema

Una vez instalado FFmpeg y las dependencias:

```bash
# Inicia el servidor
cd backend
uvicorn main:app --reload
```

Luego envía una petición POST a:
```
POST http://localhost:8000/api/test/tiktok
Content-Type: application/json

{
  "text": "La UAGRM abre nuevos cupos para el PSA. Los estudiantes interesados pueden inscribirse hasta el 30 de enero."
}
```

## 🔍 Verificar que todo funciona

Ejecuta este comando en tu terminal:

```bash
ffmpeg -version
python -c "from gtts import gTTS; print('gTTS instalado correctamente')"
```

Si ambos comandos funcionan sin errores, ¡estás listo para generar videos de TikTok!

## 💡 Notas Importantes

- Los videos se generan en formato vertical (1080x1920) para TikTok
- El audio se genera con Google TTS (gratuito, sin límites)
- Los videos de Pexels son gratuitos y libres de derechos
- Los videos se publican en modo PRIVADO por defecto para pruebas
- Los archivos temporales se limpian automáticamente después de publicar
