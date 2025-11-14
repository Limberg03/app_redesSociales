Documentación del Sistema Multi-Red Social
Tabla de Contenidos

Estrategia de Prompts
Guía de Desarrollo


Estrategia de Prompts
Objetivo
Documentar la estrategia de Prompt Engineering utilizada para instruir al Modelo de Lenguaje en la adaptación de contenido para múltiples redes sociales.
Modelo Seleccionado
Google Gemini (gemini-1.5-pro-latest)
Ventajas clave:

API robusta y confiable
Capacidad para procesar contexto extenso
Modo de salida JSON nativo (response_mime_type="application/json")
Elimina errores de parseo al garantizar respuestas JSON válidas

Estructura de Prompts
Cada prompt sigue una arquitectura de cuatro componentes:
1. Asignación de Rol (Role-Playing)
Define el contexto experto del modelo para mejorar la calidad de las respuestas.
Eres un experto en marketing de redes sociales especializado en [RED SOCIAL]
2. Definición de Tarea
Instrucción clara y específica sobre el objetivo.
Tu tarea es adaptar una noticia para ser publicada en esta plataforma
3. Restricciones y Contexto
Reglas específicas basadas en las características de cada plataforma:

Tono de comunicación
Límites de caracteres
Uso de hashtags
Frecuencia de emojis
Características especiales

4. Formato de Salida
Esquema JSON estricto con llaves escapadas ({{ y }}) para evitar conflictos con los placeholders de Python.

Prompts por Red Social
Facebook
Características:

Tono: Casual pero informativo
Límite: 63,206 caracteres
Hashtags: 2-3 opcionales
Emojis: Sí, para añadir personalidad

textEres un experto en marketing de redes sociales especializado en Facebook.
Tu tarea es adaptar una noticia para ser publicada en esta plataforma.

Características de Facebook:
- Tono: Casual pero informativo. Puede ser formal si el tema lo requiere.
- Formato: Permite texto largo (hasta 63,206 chars).
- Hashtags: Opcionales, 2-3 son suficientes.
- Emojis: Sí, úsalos para añadir personalidad.

Contenido a adaptar:
- Título: {titulo}
- Contenido: {contenido}

Debes devolver un JSON con la siguiente estructura exacta:
{{
  "text": "El texto adaptado para Facebook...",
  "hashtags": ["#Hashtag1", "#Hashtag2"],
  "character_count": 123
}}

Instagram
Características:

Tono: Visual, casual y atractivo
Límite: 2,200 caracteres
Hashtags: 5-10 (muy importantes)
Emojis: Uso generoso
Extra: Prompt para imagen generada por IA

textEres un experto en marketing de redes sociales especializado en Instagram.
Tu tarea es adaptar una noticia para ser publicada en esta plataforma.

Características de Instagram:
- Tono: Visual, casual y atractivo.
- Formato: Texto corto (hasta 2,200 chars), lo más importante va primero.
- Hashtags: Muy importantes, 5-10 son comunes.
- Emojis: Sí, úsalos generosamente.
- Especial: Sugiere un prompt para una imagen (IA generativa).

Contenido a adaptar:
- Título: {titulo}
- Contenido: {contenido}

Debes devolver un JSON con la siguiente estructura exacta:
{{
  "text": "El texto adaptado para Instagram...",
  "hashtags": ["#Hashtag1", "#Hashtag2", "#Hashtag3"],
  "character_count": 123,
  "suggested_image_prompt": "Un prompt de imagen que describa el contenido"
}}

LinkedIn
Características:

Tono: Profesional y corporativo
Límite: 3,000 caracteres
Hashtags: 3-5 relevantes a la industria
Emojis: Pocos y profesionales (📊, 📈, ✅)

textEres un experto en marketing de redes sociales especializado en LinkedIn.
Tu tarea es adaptar una noticia para ser publicada en esta plataforma.

Características de LinkedIn:
- Tono: Profesional, corporativo y orientado a la industria.
- Formato: Texto de longitud media (hasta 3,000 chars).
- Hashtags: Moderados (3-5), relevantes para la industria.
- Emojis: Pocos y profesionales (ej. 📊, 📈, ✅).

Contenido a adaptar:
- Título: {titulo}
- Contenido: {contenido}

Debes devolver un JSON con la siguiente estructura exacta:
{{
  "text": "El texto adaptado para LinkedIn...",
  "hashtags": ["#Industria", "#Profesional", "#Noticia"],
  "character_count": 123,
  "tone": "professional"
}}

TikTok
Características:

Tono: Joven, viral y directo
Límite: 2,200 caracteres (se visualiza menos)
Hashtags: Muy importantes y de tendencia
Emojis: Relacionados con tendencias
Extra: Video hook para captar atención

textEres un experto en marketing de redes sociales especializado en TikTok.
Tu tarea es adaptar una noticia para ser publicada en esta plataforma.

Características de TikTok:
- Tono: Joven, viral, directo y con gancho.
- Formato: Texto muy corto (hasta 2,200 chars, pero se ve mucho menos).
- Hashtags: Muy importantes y de tendencia.
- Emojis: Sí, relacionados con la tendencia.
- Especial: Requiere un "gancho" de video (la primera frase impactante).

Contenido a adaptar:
- Título: {titulo}
- Contenido: {contenido}

Debes devolver un JSON con la siguiente estructura exacta:
{{
  "text": "El texto adaptado para TikTok...",
  "hashtags": ["#TechTok", "#Viral", "#Noticia"],
  "character_count": 123,
  "video_hook": "La primera frase que dirías en el video para captar la atención"
}}

WhatsApp
Características:

Tono: Directo, conversacional y cercano
Formato: Texto libre con saltos de línea
Hashtags: Raros o ninguno
Emojis: Como en conversación normal

textEres un experto en comunicación directa especializado en WhatsApp.
Tu tarea es adaptar una noticia para ser enviada por este canal.

Características de WhatsApp:
- Tono: Directo, conversacional y cercano.
- Formato: Texto libre, usa saltos de línea para facilitar la lectura.
- Hashtags: Raros o ninguno.
- Emojis: Sí, como en una conversación normal.

Contenido a adaptar:
- Título: {titulo}
- Contenido: {contenido}

Debes devolver un JSON con la siguiente estructura exacta:
{{
  "text": "El texto adaptado para WhatsApp... Hola! 👋 Te cuento que...",
  "hashtags": [],
  "character_count": 123,
  "format": "conversational"
}}
```

---

## Guía de Desarrollo

### Objetivo del Módulo
Implementar el prototipo del motor de adaptación de contenido, incluyendo:
- Configuración del cliente LLM
- Servicio de adaptación
- Endpoint de API

### Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend | FastAPI |
| LLM API | Google Gemini (`google-generativeai`) |
| Validación de Datos | Pydantic |
| Variables de Entorno | `python-dotenv` |

### Estructura de Archivos
```
backend/
├── .env                # API Key de Gemini
├── main.py            # Endpoint /api/posts/adapt
├── llm_service.py     # Lógica de adaptación y prompts
└── schemas.py         # Modelos Pydantic

Componentes Principales
1. llm_service.py
Configuración del Cliente:
pythonfrom dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv()
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

generation_config = genai.GenerationConfig(
    response_mime_type="application/json",
)

model = genai.GenerativeModel(
    "gemini-1.5-pro-latest",
    generation_config=generation_config
)
Diccionario de Prompts:
pythonPROMPTS_POR_RED = {
    "facebook": "...",
    "instagram": "...",
    "linkedin": "...",
    "tiktok": "...",
    "whatsapp": "..."
}
Función de Adaptación:
pythondef adaptar_contenido(titulo: str, contenido: str, red_social: str):
    prompt_template = PROMPTS_POR_RED[red_social]
    prompt_final = prompt_template.format(
        titulo=titulo,
        contenido=contenido
    )
    
    response = model.generate_content(prompt_final)
    return json.loads(response.text)

2. schemas.py
Request Schema:
pythonfrom pydantic import BaseModel
from typing import List

class AdaptRequest(BaseModel):
    titulo: str
    contenido: str
    target_networks: List[str]
Response Schema:
pythonfrom typing import Dict, Any

class AdaptResponse(BaseModel):
    data: Dict[str, Any]

3. main.py
Endpoint de Adaptación:
pythonfrom fastapi import FastAPI
from schemas import AdaptRequest, AdaptResponse
import llm_service

app = FastAPI()

@app.post("/api/posts/adapt", response_model=AdaptResponse)
def adapt_post(request: AdaptRequest):
    adaptaciones_finales = {}
    
    for red in request.target_networks:
        resultado = llm_service.adaptar_contenido(
            request.titulo,
            request.contenido,
            red
        )
        adaptaciones_finales[red] = resultado
    
    return AdaptResponse(data=adaptaciones_finales)

Problemas Resueltos
Error: KeyError en .format()
Causa: Conflicto entre llaves del JSON de ejemplo y placeholders de Python.
Solución: Escapar llaves del JSON duplicándolas:
python# Incorrecto
"{
  "text": "..."
}"

# Correcto
"{{
  "text": "..."
}}"
```

#### Error: `429 Resource Exhausted`

**Causa:** Límite de peticiones por minuto de la API gratuita de Gemini.

**Problema:** El bucle sincrónico ejecuta 5 llamadas simultáneas.

**Solución temporal:** Añadir delays entre peticiones.

**Solución definitiva:** Implementación de **Celery con colas** (Clase 4) para:
- Procesamiento asíncrono
- Distribución de carga
- Respeto de límites de tasa

---

### Flujo de Datos
```
Cliente (Postman)
    ↓
POST /api/posts/adapt
    ↓
Validación (AdaptRequest)
    ↓
Loop sobre target_networks
    ↓
adaptar_contenido() para cada red
    ↓
Llamada a Gemini API
    ↓
Parseo de JSON
    ↓
Acumulación de resultados
    ↓
Response (AdaptResponse)