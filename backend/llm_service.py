import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    print("Cliente de Gemini configurado.")
except AttributeError:
    print("ERROR: No se encontró la variable 'GOOGLE_API_KEY' en .env")

generation_config = genai.GenerationConfig(
    response_mime_type="application/json",
)

model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    generation_config=generation_config,
)

PROMPTS_POR_RED = {
    "facebook": """
    Eres un experto en marketing de redes sociales especializado en Facebook.
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
    """,
    "instagram": """
    Eres un experto en marketing de redes sociales especializado en Instagram.
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
    """,
    "linkedin": """
    Eres un experto en marketing de redes sociales especializado en LinkedIn.
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
    """,
    "tiktok": """
    Eres un experto en marketing de redes sociales especializado en TikTok.
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
    """,
    "whatsapp": """
    Eres un experto en comunicación directa especializado en WhatsApp.
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
    """
}


import json

def adaptar_contenido(titulo: str, contenido: str, red_social: str):
    """
    Adapta el contenido para una red social específica usando Gemini.
    """
    print(f"Adaptando contenido para: {red_social}")
    
    # 1. Seleccionar el prompt correcto
    if red_social not in PROMPTS_POR_RED:
        return {"error": f"Red social '{red_social}' no soportada."}
        
    prompt_template = PROMPTS_POR_RED[red_social]
    
    # 2. Formatear el prompt con el contenido del usuario
    prompt_final = prompt_template.format(titulo=titulo, contenido=contenido)
    
    try:
        # 3. Llamar a la API de Gemini
        response = model.generate_content(prompt_final)
        
        # 4. Devolver la respuesta (que ya viene en JSON gracias a GenerationConfig)
        # El texto de la respuesta es un string JSON, necesitamos parsearlo
        response_json = json.loads(response.text)
        return response_json
        
    except Exception as e:
        print(f"Error al llamar a Gemini para {red_social}: {e}")
        return {"error": f"Error al generar contenido para {red_social}."}
