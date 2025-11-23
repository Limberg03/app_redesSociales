# CLAUDE.md - Guía Completa del Sistema Multi-Red Social

**Última actualización:** 2025-11-23
**Propósito:** Documentación para AI Assistants trabajando en este repositorio

---

## 📋 Tabla de Contenidos

1. [Resumen del Proyecto](#resumen-del-proyecto)
2. [Arquitectura General](#arquitectura-general)
3. [Estructura del Código](#estructura-del-código)
4. [Stack Tecnológico](#stack-tecnológico)
5. [Flujos de Trabajo Principales](#flujos-de-trabajo-principales)
6. [Configuración del Entorno](#configuración-del-entorno)
7. [API Endpoints](#api-endpoints)
8. [Convenciones y Estándares](#convenciones-y-estándares)
9. [Problemas Conocidos y Soluciones](#problemas-conocidos-y-soluciones)
10. [Guías para AI Assistants](#guías-para-ai-assistants)

---

## 🎯 Resumen del Proyecto

Sistema automatizado de publicación multi-red social para contenido académico de la **UAGRM** (Universidad Autónoma Gabriel René Moreno). El sistema utiliza IA (Google Gemini) para:

- **Validar** que el contenido sea académico/universitario
- **Adaptar** automáticamente el contenido al tono y formato de cada red social
- **Generar** videos con IA para TikTok (usando FFmpeg + gTTS + Pexels)
- **Publicar** simultáneamente en múltiples plataformas

### Redes Sociales Soportadas

| Red Social | Tipo de Contenido | Características Especiales |
|------------|-------------------|---------------------------|
| **Facebook** | Texto + Imágenes | Tono casual-informativo, 2-3 hashtags |
| **Instagram** | Imágenes + Caption | Visual, 5-10 hashtags, emojis generosos |
| **LinkedIn** | Texto profesional | Tono formal, profesional, networking |
| **WhatsApp** | Status con imagen | Mensajes cortos, directos, personales |
| **TikTok** | Videos verticales (1080x1920) | Generación automática de video con IA |

---

## 🏗️ Arquitectura General

```
┌─────────────────┐
│   Frontend      │  React 19 + TypeScript + Vite + Tailwind
│   (Port 5173)   │  Usuario ingresa contenido académico
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────┐
│   Backend       │  FastAPI + Python 3.11+
│   (Port 8000)   │  7 endpoints REST
└────────┬────────┘
         │
    ┌────┴────────────────────────────────┐
    │                                     │
    ▼                                     ▼
┌─────────────────┐            ┌──────────────────┐
│  LLM Service    │            │ Social Services  │
│  (Gemini 2.0)   │            │  (API Clients)   │
└────────┬────────┘            └────────┬─────────┘
         │                              │
    ┌────┴─────┐                   ┌────┴──────┐
    │          │                   │           │
    ▼          ▼                   ▼           ▼
[Validación] [Adaptación]    [Meta Graph] [TikTok API]
[Keywords]   [JSON Schema]   [WhatsApp]   [Pexels API]
                              [LinkedIn]
```

### Flujo de Datos Principal

```
1. Usuario ingresa contenido → Frontend
2. Frontend envía POST → Backend FastAPI
3. Backend valida contenido académico → Gemini LLM
4. Si válido: Adapta contenido por red social → Gemini LLM
5. Para TikTok: Genera video (FFmpeg + gTTS + Pexels)
6. Backend publica en APIs de redes sociales
7. Retorna confirmación con IDs de publicación
```

---

## 📁 Estructura del Código

```
app_redesSociales/
│
├── backend/                           # Python FastAPI Backend
│   ├── main.py                        # 🔹 Aplicación FastAPI principal
│   │                                  # - 7 endpoints REST
│   │                                  # - CORS middleware configurado
│   │                                  # - Validación con Pydantic
│   │
│   ├── llm_service.py                 # 🔹 Servicio de IA (Gemini)
│   │                                  # - adaptar_contenido() → Adapta texto por red
│   │                                  # - validar_contenido_academico() → Valida temas UAGRM
│   │                                  # - generar_video_tiktok() → Pipeline completo de video
│   │                                  # - extraer_keywords() → Extrae 3 palabras clave
│   │                                  # - buscar_videos_pexels() → Busca videos de stock
│   │                                  # - combinar_videos_con_audio() → FFmpeg processing
│   │
│   ├── social_services.py             # 🔹 Clientes de APIs sociales
│   │                                  # - post_to_facebook()
│   │                                  # - post_to_instagram()
│   │                                  # - post_to_linkedin()
│   │                                  # - post_to_whatsapp()
│   │                                  # - upload_to_tiktok()
│   │
│   ├── schemas.py                     # 🔹 Modelos Pydantic
│   │                                  # - AdaptRequest, AdaptResponse
│   │                                  # - TestPostRequest, TestPostRequestLinkedIn
│   │
│   ├── requirements.txt               # 🔹 Dependencias Python
│   │                                  # Ver sección "Stack Tecnológico"
│   │
│   ├── .env                           # 🔹 Variables de entorno (NO en Git)
│   │                                  # GOOGLE_API_KEY, PEXELS_API_KEY, etc.
│   │
│   ├── SETUP_TIKTOK.md               # 📖 Guía de instalación FFmpeg
│   ├── Desarrollo.md                  # 📖 Documentación de desarrollo
│   ├── Prompt.md                      # 📖 Estrategia de Prompt Engineering
│   │
│   └── test_*.py                      # 🧪 Scripts de prueba
│       ├── test_validacion_academica.py
│       ├── test_elevenlabs.py
│       └── ...
│
└── frontend/                          # React + TypeScript Frontend
    ├── src/
    │   ├── App.tsx                    # 🔹 Componente principal React
    │   │                              # - Formulario de entrada
    │   │                              # - Selección de redes sociales
    │   │                              # - Llamadas Axios al backend
    │   │
    │   ├── App.css                    # 🎨 Estilos principales
    │   └── assets/                    # 📦 Recursos estáticos
    │
    ├── public/                        # 📦 Assets públicos
    ├── index.html                     # 🔹 Entry point HTML
    │
    ├── package.json                   # 🔹 Dependencias NPM
    ├── vite.config.ts                 # ⚙️ Configuración Vite
    ├── tsconfig.json                  # ⚙️ Configuración TypeScript
    └── tailwind.config.js             # ⚙️ Configuración Tailwind CSS
```

---

## 🛠️ Stack Tecnológico

### Backend (Python)

#### Core Framework
- **FastAPI 0.121.1** - Framework web moderno con auto-documentación (Swagger)
- **Uvicorn 0.38.0** - Servidor ASGI de alto rendimiento
- **Pydantic 2.12.4** - Validación de datos y serialización

#### IA y Procesamiento de Lenguaje
- **google-generativeai 0.8.5** - SDK oficial de Google Gemini
  - Modelo usado: `gemini-2.0-flash-exp` (rápido, económico)
  - Capacidades: JSON mode nativo, context window grande
  - Funciones: Validación, adaptación, extracción de keywords

#### Generación de Video (TikTok)
- **FFmpeg** - Procesamiento de video (REQUERIDO en PATH del sistema)
  - Concatenación de múltiples videos
  - Escalado a 1080x1920 (vertical)
  - Mixing de audio y video
- **ffmpeg-python** - Wrapper Python para FFmpeg
- **gTTS 2.5.4** - Google Text-to-Speech (audio gratuito, sin límites)
- **httpx 0.28.1** - Cliente HTTP async para descargar videos de Pexels

#### APIs de Redes Sociales
- **Meta Graph API** - Facebook + Instagram
- **TikTok Open API** - Upload de videos
- **LinkedIn API** - Publicaciones profesionales
- **WhatsApp Cloud API (via Twilio)** - Status updates
- **Pexels API** - Videos de stock gratuitos

#### Procesamiento Asíncrono
- **Celery 5.5.3** - Task queue para trabajos pesados
- **Redis 7.0.1** - Message broker para Celery
- **aiohttp 3.13.2** - Cliente HTTP asíncrono

#### Base de Datos
- **SQLAlchemy 2.0.44** - ORM
- **psycopg2-binary 2.9.11** - Driver PostgreSQL
- **Alembic 1.17.1** - Migraciones de DB

#### Autenticación y Seguridad
- **PyJWT 2.10.1** - JSON Web Tokens
- **google-auth 2.43.0** - OAuth2 para Google APIs

### Frontend (JavaScript/TypeScript)

#### Core Framework
- **React 19.2.0** - UI library moderna
- **TypeScript 5.9.3** - Type safety
- **Vite 7.2.2** - Build tool ultra-rápido

#### UI/UX
- **Tailwind CSS 4.1.17** - Utility-first CSS framework
- **React Router 7.9.5** - Client-side routing

#### HTTP Client
- **Axios 1.13.2** - Llamadas HTTP al backend

---

## 🔄 Flujos de Trabajo Principales

### 1. Adaptación Multi-Red (Endpoint `/api/posts/adapt`)

```python
# Flujo interno en llm_service.py

def adaptar_contenido(titulo: str, contenido: str, red_social: str) -> dict:
    """
    Paso 1: Seleccionar prompt por red social
    - Facebook: Casual, 2-3 hashtags
    - Instagram: Visual, 5-10 hashtags
    - LinkedIn: Profesional, formal
    - TikTok: Joven, viral, dinámico
    - WhatsApp: Personal, directo
    """
    prompt = PROMPTS_POR_RED[red_social].format(
        titulo=titulo,
        contenido=contenido
    )

    """
    Paso 2: Enviar a Gemini con JSON mode
    - response_mime_type="application/json"
    - Garantiza respuesta JSON válida
    """
    response = model.generate_content(prompt)

    """
    Paso 3: Parsear respuesta JSON
    Estructura esperada:
    {
      "text": "Texto adaptado...",
      "hashtags": ["#Tag1", "#Tag2"],
      "character_count": 150
    }

    Para Instagram añade:
      "image_prompt": "Prompt para generar imagen con IA..."
    """
    return json.loads(response.text)
```

**Características por Red:**

| Red | Límite Caracteres | Hashtags | Emojis | Especial |
|-----|------------------|----------|--------|----------|
| Facebook | 63,206 | 2-3 | Moderado | Permite texto largo |
| Instagram | 2,200 | 5-10 | Generoso | Incluye image_prompt |
| LinkedIn | ~3,000 | 0-2 | Mínimo | Tono profesional |
| TikTok | 150 (caption) | 3-5 | Alto | Texto viral, joven |
| WhatsApp | 700 | 1-2 | Moderado | Directo, personal |

### 2. Validación de Contenido Académico

```python
def validar_contenido_academico(texto: str) -> dict:
    """
    Valida que el contenido sea relacionado con UAGRM

    Temas permitidos:
    - Fechas académicas (inicio de clases, exámenes, inscripciones)
    - Eventos universitarios (conferencias, seminarios, talleres)
    - Anuncios administrativos (becas, PSA, matrículas)
    - Actividades estudiantiles (ferias, competencias, proyectos)
    - Logros académicos (graduaciones, reconocimientos)

    Returns:
        {
          "es_academico": true/false,
          "razon": "Explicación de la decisión",
          "categoria": "fechas_academicas" | "eventos" | "otro"
        }
    """
```

**Ejemplo de rechazo:**
```json
{
  "es_academico": false,
  "razon": "El contenido trata sobre política electoral, no es relevante para actividades universitarias",
  "categoria": "no_academico"
}
```

### 3. Generación de Video TikTok (Pipeline Completo)

**Archivo:** `llm_service.py` líneas 578-626

```python
def generar_video_tiktok(texto_adaptado: str) -> str:
    """
    🎬 PIPELINE COMPLETO DE GENERACIÓN DE VIDEO

    PASO 1: Extraer Keywords
    ========================
    - Envía texto a Gemini
    - Pide 3 palabras clave en INGLÉS
    - Formato: ["students", "university", "education"]
    """
    keywords = extraer_keywords(texto_adaptado)

    """
    PASO 2: Buscar Videos en Pexels
    ================================
    - Busca videos para cada keyword
    - Filtros aplicados:
      * orientation=portrait (vertical)
      * size=medium
      * per_page=1
    - Descarga URLs de videos
    """
    video_urls = buscar_videos_pexels(keywords)

    """
    PASO 3: Generar Audio con gTTS
    ===============================
    - Convierte texto_adaptado a audio MP3
    - Idioma: Español (lang='es')
    - Guarda en archivo temporal
    """
    audio_path = generar_audio_gtts(texto_adaptado)

    """
    PASO 4: Combinar Videos + Audio (FFmpeg)
    =========================================
    Ver función combinar_videos_con_audio() más abajo
    """
    video_final = combinar_videos_con_audio(
        video_urls=video_urls,
        audio_path=audio_path,
        duracion_total=15  # 15 segundos max
    )

    """
    PASO 5: Cleanup
    ===============
    - Elimina audio temporal
    - Retorna path del video final
    """
    return video_final


def combinar_videos_con_audio(video_urls: list, audio_path: str, duracion_total: int = 15) -> str:
    """
    🎥 PROCESAMIENTO FFMPEG

    ETAPA 1: Verificar FFmpeg instalado
    ===================================
    """
    if not verificar_ffmpeg():
        raise Exception("FFmpeg no está instalado")

    """
    ETAPA 2: Descargar videos de Pexels
    ====================================
    - Descarga cada video_url con httpx
    - Guarda en archivos temporales .mp4
    """
    video_paths = []
    for url in video_urls:
        response = httpx.get(url, timeout=30.0)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(response.content)
        video_paths.append(temp_file.name)

    """
    ETAPA 3: Crear archivo de concatenación
    ========================================
    - Crea concat.txt con lista de videos
    - Formato: file '/path/to/video1.mp4'
    - Escapa barras invertidas en Windows
    """
    concat_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
    for path in video_paths:
        path_escaped = path.replace('\\', '/')
        concat_file.write(f"file '{path_escaped}'\n")
    concat_file.close()

    """
    ETAPA 4: Concatenar videos con FFmpeg
    ======================================
    Comando:
      ffmpeg -f concat -safe 0 -i concat.txt \
             -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
             -t 15 \
             -c:v libx264 -preset fast \
             -y temp_video.mp4

    Explicación:
    - -f concat: Concatenar múltiples archivos
    - -safe 0: Permitir rutas absolutas
    - -vf scale: Escalar a 1080x1920 (TikTok vertical)
    - crop: Recortar para mantener aspect ratio
    - -t 15: Limitar a 15 segundos
    - -c:v libx264: Codec H.264
    - -preset fast: Balance velocidad/calidad
    """
    subprocess.run([
        'ffmpeg', '-f', 'concat', '-safe', '0',
        '-i', concat_file.name,
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
        '-t', str(duracion_total),
        '-c:v', 'libx264', '-preset', 'fast',
        '-y', temp_video
    ], check=True, capture_output=True)

    """
    ETAPA 5: Agregar audio con FFmpeg
    ==================================
    Comando:
      ffmpeg -i temp_video.mp4 -i audio.mp3 \
             -c:v copy -c:a aac \
             -map 0:v:0 -map 1:a:0 \
             -shortest \
             -y output.mp4

    Explicación:
    - -c:v copy: No re-encodear video (rápido)
    - -c:a aac: Encodear audio a AAC
    - -map 0:v:0: Usar video del primer input
    - -map 1:a:0: Usar audio del segundo input
    - -shortest: Terminar cuando el stream más corto termine
    """
    subprocess.run([
        'ffmpeg', '-i', temp_video, '-i', audio_path,
        '-c:v', 'copy', '-c:a', 'aac',
        '-map', '0:v:0', '-map', '1:a:0',
        '-shortest',
        '-y', output_path
    ], check=True, capture_output=True)

    """
    ETAPA 6: Cleanup y retorno
    ===========================
    """
    os.unlink(concat_file.name)
    os.unlink(temp_video)
    for path in video_paths:
        os.unlink(path)

    return output_path
```

**Requisitos del Sistema:**
1. **FFmpeg** debe estar instalado y en PATH
2. **gTTS** debe estar instalado (`pip install gTTS==2.5.4`)
3. **PEXELS_API_KEY** en `.env`
4. **TIKTOK_ACCESS_TOKEN** en `.env` para publicación

### 4. Publicación en TikTok

```python
# Archivo: social_services.py

def upload_to_tiktok(video_path: str, caption: str) -> dict:
    """
    Paso 1: Inicializar upload
    - POST a /v2/post/publish/video/init/
    - Obtener publish_id
    """

    """
    Paso 2: Upload de video
    - POST video file en chunks
    - Formato: multipart/form-data
    """

    """
    Paso 3: Confirmar publicación
    - Enviar caption y configuración
    - privacy_level: "SELF_ONLY" (privado por defecto)
    - disable_comment: true (comentarios deshabilitados)
    """

    return {
        "publish_id": "...",
        "share_url": "https://www.tiktok.com/@usuario/video/...",
        "status": "published"
    }
```

---

## ⚙️ Configuración del Entorno

### Variables de Entorno Requeridas

Crear archivo `/backend/.env`:

```bash
# IA - Google Gemini
GOOGLE_API_KEY=AIzaSy...           # Obtener en https://makersuite.google.com/app/apikey

# Videos de Stock
PEXELS_API_KEY=abc123...           # Obtener en https://www.pexels.com/api/

# Facebook + Instagram (Meta)
META_ACCESS_TOKEN=EAAabc...        # Token de larga duración (60 días)
FACEBOOK_PAGE_ID=123456789         # ID de la página de Facebook
INSTAGRAM_ACCOUNT_ID=987654321    # ID de cuenta profesional de Instagram

# TikTok
TIKTOK_ACCESS_TOKEN=act.xyz...     # Token OAuth2 (usar get_tiktok_token.py)

# WhatsApp Business (via Twilio o WhatsApp Cloud API)
WHAPI_TOKEN=whapi_token...         # Token de WhatsApp Business API
WHAPI_CHANNEL_ID=channel_id...     # ID del canal de WhatsApp

# LinkedIn (Opcional)
LINKEDIN_ACCESS_TOKEN=AQVabc...    # OAuth2 token

# Base de Datos (Opcional - para producción)
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

### Instalación del Backend

```bash
# 1. Navegar al directorio backend
cd backend

# 2. Crear entorno virtual (recomendado)
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar FFmpeg (CRÍTICO para TikTok)
# Windows: Ver sección "Problemas Conocidos" más abajo
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# 5. Verificar instalación de FFmpeg
ffmpeg -version

# 6. Crear archivo .env con las variables de arriba

# 7. Ejecutar servidor
uvicorn main:app --reload

# Servidor corriendo en: http://localhost:8000
# Documentación Swagger: http://localhost:8000/docs
```

### Instalación del Frontend

```bash
# 1. Navegar al directorio frontend
cd frontend

# 2. Instalar dependencias
npm install

# 3. Ejecutar en modo desarrollo
npm run dev

# 4. Build para producción
npm run build

# Frontend corriendo en: http://localhost:5173
```

---

## 🌐 API Endpoints

### Documentación Interactiva
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints Disponibles

#### 1. Health Check
```http
GET /
```
**Respuesta:**
```json
{
  "message": "API del Sistema Multi-Red Social funcionando"
}
```

---

#### 2. Adaptar Contenido (Multi-Red)
```http
POST /api/posts/adapt
Content-Type: application/json
```

**Request Body:**
```json
{
  "titulo": "UAGRM abre nuevos cupos para el PSA",
  "contenido": "La universidad anuncia 500 cupos adicionales para el Proceso de Selección Académica. Las inscripciones estarán abiertas hasta el 30 de enero.",
  "target_networks": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
}
```

**Response:**
```json
{
  "data": {
    "facebook": {
      "text": "🎓 ¡Nuevas oportunidades en la UAGRM! 🚀\n\nLa universidad ha anunciado 500 cupos adicionales...",
      "hashtags": ["#UAGRM", "#PSA"],
      "character_count": 245
    },
    "instagram": {
      "text": "🔥 ¡ATENCIÓN FUTUROS UNIVERSITARIOS! 🎯\n\n500 NUEVOS CUPOS para el PSA...",
      "hashtags": ["#UAGRM", "#PSA2025", "#UniversidadBolivia", "#Educacion", "#Estudiantes"],
      "image_prompt": "University campus with happy students celebrating, modern architecture, bright colors",
      "character_count": 198
    },
    "tiktok": {
      "text": "🚨¡ÚLTIMA HORA UAGRM!🚨 ¿Quieres entrar a la U? 🔥 ¡500 nuevos cupos PSA! 😱 Inscríbete YA...",
      "hashtags": ["#UAGRM", "#PSA", "#UniversidadBolivia", "#FYP"],
      "character_count": 142
    }
    // ... otras redes
  }
}
```

---

#### 3. Publicar en Facebook (CON validación académica)
```http
POST /api/test/facebook
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "La UAGRM realizará una feria de ciencias el próximo viernes en el campus universitario."
}
```

**Response (éxito):**
```json
{
  "platform": "facebook",
  "status": "published",
  "post_id": "123456789_987654321",
  "message": "✅ Publicado en Facebook (solo texto)",
  "adapted_text": "🔬 ¡Feria de Ciencias UAGRM! 🎓\n\nEste viernes nos vemos en el campus...",
  "post_url": "https://www.facebook.com/123456789_987654321"
}
```

**Response (contenido no académico):**
```json
{
  "error": "contenido_no_academico",
  "mensaje": "❌ Este contenido no es apropiado para publicación académica. Por favor, ingrese información relacionada con actividades universitarias..."
}
```

---

#### 4. Publicar en Instagram (CON validación + imagen)
```http
POST /api/test/instagram
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Conferencia sobre inteligencia artificial en la UAGRM",
  "image_url": "https://example.com/poster-conferencia.jpg"
}
```

**Response:**
```json
{
  "platform": "instagram",
  "status": "published",
  "media_id": "17895695668082849",
  "adapted_text": "🤖 IA en la UAGRM! 🚀\n\nNo te pierdas esta conferencia...",
  "hashtags": ["#UAGRM", "#InteligenciaArtificial", "#Tech", "#Bolivia"]
}
```

---

#### 5. Publicar en LinkedIn (Profesional)
```http
POST /api/test/linkedin
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "La UAGRM firma convenio de cooperación internacional con universidades europeas"
}
```

**Response:**
```json
{
  "platform": "linkedin",
  "status": "published",
  "post_id": "urn:li:share:1234567890",
  "adapted_text": "Nos complace anunciar la firma de un convenio de cooperación internacional..."
}
```

---

#### 6. Publicar en WhatsApp Status
```http
POST /api/test/whatsapp
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "Recordatorio: Inscripciones PSA cierran mañana",
  "image_url": "https://example.com/reminder.jpg"
}
```

---

#### 7. Generar y Publicar Video TikTok ⭐
```http
POST /api/test/tiktok
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "La UAGRM anuncia 500 nuevos cupos para el PSA. ¡No pierdas esta oportunidad de ingresar a la universidad!"
}
```

**Response (éxito):**
```json
{
  "platform": "tiktok",
  "status": "published",
  "publish_id": "v_pub_abc123xyz",
  "share_url": "https://www.tiktok.com/@uagrm/video/7123456789",
  "caption": "🚨¡ÚLTIMA HORA UAGRM!🚨 ¿Quieres entrar a la U? 🔥 ¡500 nuevos cupos PSA! 😱",
  "video_duration": 15,
  "message": "✅ Video generado y publicado en TikTok"
}
```

**Response (error FFmpeg):**
```json
{
  "error": "ffmpeg_not_found",
  "detail": "FFmpeg no está instalado o no está en el PATH. Ver SETUP_TIKTOK.md"
}
```

---

## 📏 Convenciones y Estándares

### Estilo de Código Python

1. **Formato**: PEP 8 (líneas de 88 caracteres máx con Black)
2. **Type Hints**: Usar siempre en funciones públicas
   ```python
   def adaptar_contenido(titulo: str, contenido: str, red_social: str) -> dict:
   ```

3. **Docstrings**: Google Style
   ```python
   def funcion(parametro: str) -> dict:
       """
       Descripción breve de la función.

       Args:
           parametro: Descripción del parámetro

       Returns:
           dict: Estructura de la respuesta

       Raises:
           HTTPException: Cuando ocurre un error
       """
   ```

4. **Nombres de Variables**:
   - `snake_case` para funciones y variables
   - `PascalCase` para clases
   - `UPPER_CASE` para constantes

   ```python
   PROMPTS_POR_RED = {...}

   def validar_contenido_academico(texto: str) -> dict:
       es_valido = True
   ```

### Estructura de Respuestas API

**Éxito:**
```json
{
  "platform": "nombre_red",
  "status": "published",
  "post_id": "id_plataforma",
  "adapted_text": "Texto usado...",
  "post_url": "URL del post"
}
```

**Error:**
```json
{
  "error": "codigo_error",
  "detail": "Mensaje descriptivo",
  "mensaje": "Mensaje amigable al usuario (español)"
}
```

### Manejo de Errores

1. **Validación de entrada**: `HTTPException` con código 400
   ```python
   if not validacion.get("es_academico"):
       raise HTTPException(
           status_code=400,
           detail={"error": "contenido_no_academico", ...}
       )
   ```

2. **Errores de API externa**: Capturar y retornar mensaje claro
   ```python
   try:
       response = httpx.post(...)
   except httpx.RequestError as e:
       return {"error": str(e)}
   ```

3. **Logging**: Usar `print()` con emojis para debugging
   ```python
   print("🔍 [TikTok] Validando contenido académico...")
   print(f"✅ Video encontrado: {keyword}")
   print(f"❌ Error en FFmpeg: {e.stderr}")
   ```

### Convenciones de Frontend (React)

1. **Componentes**: PascalCase, un componente por archivo
2. **Props**: Destructuring en parámetros
3. **State**: `useState` con nombres descriptivos
4. **Estilos**: Tailwind utility classes preferiblemente

---

## 🚨 Problemas Conocidos y Soluciones

### Problema 1: FFmpeg no encontrado (Windows)

**Error:**
```
❌ FFmpeg no está instalado o no está en el PATH
❌ Error combinando videos: [WinError 2] El sistema no puede encontrar el archivo especificado
INFO: 127.0.0.1:56484 - "POST /api/test/tiktok HTTP/1.1" 500 Internal Server Error
```

**Causa:**
FFmpeg no está instalado o no está accesible desde la variable de entorno PATH en Windows.

**Solución (Windows):**

1. **Descargar FFmpeg:**
   - Ir a: https://www.gyan.dev/ffmpeg/builds/
   - Descargar: `ffmpeg-release-essentials.zip` (110 MB aprox)
   - Extraer a una ubicación permanente: `C:\ffmpeg`

2. **Agregar al PATH del Sistema:**
   - Presionar `Win + R`, escribir `sysdm.cpl`, Enter
   - Ir a pestaña "Opciones avanzadas"
   - Click en "Variables de entorno"
   - En "Variables del sistema", buscar `Path`
   - Click "Editar" → "Nuevo"
   - Agregar: `C:\ffmpeg\bin`
   - Click "Aceptar" en todas las ventanas

3. **REINICIAR el terminal/IDE:**
   - Es crítico reiniciar para que tome los cambios de PATH
   - Cerrar VS Code, PyCharm, cmd, etc.
   - Volver a abrir

4. **Verificar instalación:**
   ```bash
   # Debe mostrar la versión de FFmpeg
   ffmpeg -version

   # Debe mostrar: ffmpeg version N-xxxxx...
   ```

5. **Verificar desde Python:**
   ```bash
   python -c "import subprocess; subprocess.run(['ffmpeg', '-version'])"
   ```

**Solución alternativa (Docker):**

Si el problema persiste en Windows, considerar usar Docker:

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Instalar FFmpeg en el contenedor
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Construir y ejecutar
docker build -t app-redes .
docker run -p 8000:8000 --env-file backend/.env app-redes
```

**Verificación del problema:**

El código verifica FFmpeg antes de usarlo (`llm_service.py:468-483`):

```python
def verificar_ffmpeg() -> bool:
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False  # FFmpeg no está en PATH
    except Exception:
        return False
```

---

### Problema 2: Tokens OAuth Expirados

**Error:**
```json
{"error": "invalid_token", "detail": "The access token is expired"}
```

**Solución:**

1. **Facebook/Instagram (60 días):**
   ```bash
   cd backend
   python get_tokens.py
   # Seguir instrucciones para renovar token
   ```

2. **TikTok (OAuth2):**
   ```bash
   cd backend
   python get_tiktok_token.py
   # Abrirá navegador para autorizar
   ```

3. Actualizar `.env` con los nuevos tokens

---

### Problema 3: Videos de Pexels no verticales

**Síntoma:** Videos horizontales en TikTok se ven cortados

**Causa:** Pexels no siempre tiene videos en orientación portrait

**Solución parcial:**
El código ya aplica `scale` y `crop` en FFmpeg para forzar 1080x1920:

```python
# llm_service.py:537
'-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920'
```

**Mejora futura:**
Filtrar mejor en la búsqueda de Pexels:

```python
# Agregar validación de aspect ratio
videos = pexels_api.search(query, orientation='portrait', size='medium')
videos_validos = [v for v in videos if v.height > v.width]
```

---

### Problema 4: gTTS Audio muy largo (>15 segundos)

**Síntoma:** El audio es más largo que los videos disponibles

**Solución actual:**
FFmpeg usa `-shortest` para cortar al stream más corto:

```python
# llm_service.py:549
'-shortest'  # Terminar cuando el video o audio más corto termine
```

**Mejora futura:**
Limitar el texto adaptado para TikTok:

```python
# En el prompt de TikTok
"El texto debe ser máximo 100 caracteres para que el audio no exceda 15 segundos"
```

---

### Problema 5: Rate Limits de APIs

**Síntoma:** Errores 429 (Too Many Requests)

**Soluciones:**

1. **Pexels:** 200 requests/hora (gratis)
   - Implementar cache de videos ya usados
   - Esperar 1 segundo entre requests

2. **Meta Graph API:** Varía por endpoint
   - Usar exponential backoff en errores
   - Monitorear headers `X-App-Usage`

3. **Gemini:** 60 requests/minuto (gratis)
   - Implementar rate limiter con Redis
   - Usar Celery para encolar requests

---

## 🤖 Guías para AI Assistants

### Cuando Modificar el Backend

1. **Nuevas Redes Sociales:**
   - Agregar prompt en `llm_service.py` → `PROMPTS_POR_RED`
   - Crear función en `social_services.py` → `post_to_[red]()`
   - Agregar endpoint en `main.py` → `@app.post("/api/test/[red]")`
   - Documentar en este archivo (CLAUDE.md)

2. **Cambiar Comportamiento del LLM:**
   - Modificar prompts en `PROMPTS_POR_RED`
   - Ajustar parsing del JSON en `adaptar_contenido()`
   - **SIEMPRE** probar con `test_validacion_academica.py`

3. **Nuevas Features de Video:**
   - Modificar `generar_video_tiktok()` en `llm_service.py`
   - **VERIFICAR** que FFmpeg esté instalado antes de testear
   - Documentar nuevos parámetros de FFmpeg

### Cuando Modificar el Frontend

1. **Nueva Red Social en UI:**
   - Agregar checkbox en `App.tsx`
   - Actualizar type `target_networks` en TypeScript
   - Manejar respuesta en `axios.post().then()`

2. **Nuevos Campos de Formulario:**
   - Agregar `useState` en `App.tsx`
   - Actualizar `schemas.py` con nuevo campo Pydantic
   - Actualizar endpoint correspondiente en `main.py`

### Flujo de Debugging

1. **Error en Adaptación:**
   ```bash
   # Ver qué prompt se está usando
   grep -A 20 "PROMPTS_POR_RED\[\"tiktok\"\]" backend/llm_service.py

   # Probar manualmente
   cd backend
   python -c "from llm_service import adaptar_contenido; print(adaptar_contenido('test', 'contenido test', 'tiktok'))"
   ```

2. **Error en Video TikTok:**
   ```bash
   # Verificar FFmpeg
   ffmpeg -version

   # Ver logs de FFmpeg
   cd backend
   python -c "from llm_service import combinar_videos_con_audio; combinar_videos_con_audio(['url1', 'url2'], 'audio.mp3')"
   ```

3. **Error en APIs Sociales:**
   ```bash
   # Probar token manualmente
   curl -X GET "https://graph.facebook.com/v18.0/me?access_token=YOUR_TOKEN"

   # Ver error completo
   cd backend
   python -c "from social_services import post_to_facebook; print(post_to_facebook('test', None))"
   ```

### Mejores Prácticas

1. **NUNCA** hardcodear tokens en el código
2. **SIEMPRE** validar contenido académico antes de publicar
3. **SIEMPRE** usar `try-except` en llamadas a APIs externas
4. **SIEMPRE** limpiar archivos temporales después de generar videos
5. **NUNCA** commitear archivos `.env` al repositorio
6. **SIEMPRE** documentar nuevos prompts en `Prompt.md`
7. **SIEMPRE** actualizar `requirements.txt` si se agregan dependencias

### Testing

```bash
# Backend - Validación académica
cd backend
python test_validacion_academica.py

# Backend - Server
uvicorn main:app --reload

# Frontend - Development
cd frontend
npm run dev

# Frontend - Build
npm run build
npm run preview

# Integración - Probar endpoint
curl -X POST http://localhost:8000/api/posts/adapt \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Test","contenido":"La UAGRM...","target_networks":["facebook"]}'
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- **FastAPI:** https://fastapi.tiangolo.com/
- **Google Gemini:** https://ai.google.dev/docs
- **FFmpeg:** https://ffmpeg.org/documentation.html
- **gTTS:** https://gtts.readthedocs.io/
- **Pexels API:** https://www.pexels.com/api/documentation/
- **Meta Graph API:** https://developers.facebook.com/docs/graph-api
- **TikTok API:** https://developers.tiktok.com/

### Archivos de Documentación Interna

- `/backend/SETUP_TIKTOK.md` - Guía de instalación FFmpeg
- `/backend/Desarrollo.md` - Estrategia de Prompt Engineering
- `/backend/Prompt.md` - Prompts detallados por red social

### Estructura de Prompts (Gemini)

Todos los prompts siguen esta estructura:

```
1. ROLE-PLAYING: "Eres un experto en marketing de [RED SOCIAL]..."
2. TAREA: "Tu tarea es adaptar una noticia..."
3. CARACTERÍSTICAS: Tono, límites, hashtags, emojis
4. RESTRICCIONES: "DEBES respetar el límite de caracteres..."
5. FORMATO: Esquema JSON con llaves escapadas {{ }}
```

Ver ejemplos completos en `/backend/Prompt.md`

---

## 🔄 Changelog del Sistema

### v2.0 (Actual) - TikTok Video Generation
- ✅ Generación automática de videos con FFmpeg
- ✅ Audio con gTTS (Google TTS gratuito)
- ✅ Videos de Pexels con keywords extraídas por IA
- ✅ Validación de contenido académico en TODOS los endpoints
- ✅ Adaptación automática antes de publicar

### v1.0 - Sistema Multi-Red Base
- ✅ Adaptación de contenido con Gemini
- ✅ Publicación en Facebook, Instagram, LinkedIn, WhatsApp
- ✅ Frontend React con Tailwind
- ✅ Backend FastAPI con Pydantic

---

## 📞 Contacto y Soporte

**Repositorio:** Limberg03/app_redesSociales
**Branch actual:** `claude/claude-md-mic478g4p9js3w5j-01URthubcGeMXfksD1ydQDfL`
**Main branch:** Pendiente definir

Para reportar bugs o solicitar features, contactar al equipo de desarrollo.

---

**Última actualización:** 2025-11-23
**Mantenido por:** AI Assistant Claude + Equipo de Desarrollo UAGRM
