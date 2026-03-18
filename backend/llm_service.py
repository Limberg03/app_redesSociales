import os
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
import tempfile
import re
import shutil
import platform

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

# ============================================
# 🔧 CONFIGURACIÓN DE FFMPEG
# ============================================

# CONFIGURACIÓN ESPECÍFICA PARA TU SISTEMA
if platform.system() == "Windows":
    # 🎯 TU RUTA ESPECÍFICA DE FFMPEG
    FFMPEG_PATH = r"C:\ffmpeg-8.0.1-full_build\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe"
    
    # Verificar que existe
    if not os.path.exists(FFMPEG_PATH):
        print(f"⚠️ FFmpeg no encontrado en ruta específica: {FFMPEG_PATH}")
        print("🔍 Buscando en PATH del sistema...")
        FFMPEG_PATH = shutil.which('ffmpeg') or 'ffmpeg'
    else:
        print(f"FFmpeg configurado correctamente: {FFMPEG_PATH}")
else:
    # Linux/Mac: usar PATH normal
    FFMPEG_PATH = shutil.which('ffmpeg') or 'ffmpeg'
    print(f"🎬 Usando FFmpeg desde PATH: {FFMPEG_PATH}")

# ============================================

PROMPTS_POR_RED = {
    "facebook": """
    Eres un experto en marketing de redes sociales especializado en Facebook para instituciones académicas.
    Tu tarea es adaptar contenido académico/universitario para ser publicado en esta plataforma.

    Características de Facebook para instituciones académicas:
    - Tono: Profesional pero cercano, informativo y claro.
    - Formato: Permite texto largo (hasta 63,206 chars).
    - Hashtags: 2-3 hashtags relevantes (siempre incluir #UAGRM si es apropiado).
    - Emojis: Sí, úsalos moderadamente para añadir personalidad (📚 🎓 📅 ✅ 🎯).
    - Enfoque: Información clara y útil para estudiantes.

    Contenido a adaptar:
    - Título: {titulo}
    - Contenido: {contenido}

    Debes devolver un JSON con la siguiente estructura exacta:
    {{
      "text": "El texto adaptado para Facebook con estilo académico...",
      "hashtags": ["#UAGRM", "#Universidad"],
      "character_count": 123,
      "suggested_image_prompt": "Un prompt de imagen que describa el contenido académico para Facebook"
    }}
    """,
    "instagram": """
    Eres un experto en marketing de redes sociales especializado en Instagram para instituciones académicas.
    Tu tarea es adaptar contenido académico/universitario para ser publicado en esta plataforma.

    Características de Instagram para instituciones académicas:
    - Tono: Visual, dinámico, juvenil pero profesional.
    - Formato: Texto corto y directo (hasta 2,200 chars), lo más importante va primero.
    - Hashtags: Muy importantes, 5-8 hashtags (siempre incluir #UAGRM y hashtags académicos).
    - Emojis: Sí, úsalos generosamente pero con buen gusto (📚 🎓 ✨ 🚀 📅 🎯).
    - Enfoque: Captar atención rápidamente, estilo más visual y energético.

    Contenido a adaptar:
    - Título: {titulo}
    - Contenido: {contenido}

    Debes devolver un JSON con la siguiente estructura exacta:
    {{
      "text": "El texto adaptado para Instagram con estilo académico dinámico...",
      "hashtags": ["#UAGRM", "#Universidad", "#EstudiantesUAGRM", "#VidaUniversitaria", "#Educacion"],
      "character_count": 123,
      "suggested_image_prompt": "Un prompt de imagen que describa el contenido académico"
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
    Tu tarea es adaptar COMPLETAMENTE una noticia académica para ser publicada en esta plataforma.

    CARACTERÍSTICAS DE TIKTOK:
    ✅ Tono: Joven, viral, directo, con gancho, conversacional
    ✅ Formato: Texto SHORT pero COMPLETO (máximo 2,200 chars, pero idealmente 150-300 chars para el post + video hook)
    ✅ Emojis: SÍ, muchos emojis relacionados con el tema (📚 🎓 ✨ 🚀 ⚡ 🔔 ⏰ 📢 🤯)
    ✅ Hashtags: CRÍTICOS - Incluir 5-8 hashtags de tendencia + #UAGRM
    ✅ Video Hook: ESENCIAL - La primera frase debe ser IMPACTANTE para captar en los primeros 2 segundos

    ⭐ REGLA CRÍTICA: El "text" debe ser COMPLETO y COHERENTE:
    - Inicia con un emoji de atención o urgencia si es relevante
    - Desarrolla el contenido principal de forma clara
    - Mantén el mensaje del usuario original
    - Termina con un llamado a la acción o pregunta
    - NO hagas el texto demasiado corto (mínimo 60-80 caracteres de contenido real)

    ⭐ REGLA PARA tts_text (INTERPRETACIÓN DE SIGLAS):
    - FICCT SIEMPRE debe interpretarse como "Facultad de Ingeniería de Ciencias de la Computación"
    - UAGRM SIEMPRE debe interpretarse como "Universidad Autónoma Gabriel René Moreno"
    - NO repitas el nombre de la facultad/universidad dos veces en la misma narración
    - Usa pronombres de referencia: "La facultad", "Esta institución", "Allí" después de la primera mención
    - NO uses frases informales: "Participa y comparte tu opinión", "Comenta abajo"
    - USA frases profesionales: "Verifica los detalles", "No te lo pierdas", "Marca tu calendario"
    - NO repitas "Facultad de Ingeniería de Ciencias de la Computación" múltiples veces
    - Después de la primera mención, usa: "la facultad", "esta carrera", "el área"
    - Ejemplo: "La Facultad de Ingeniería de Ciencias de la Computación anuncia... En la facultad habrá..."

    Contenido a adaptar:
    - Título: {titulo}
    - Contenido: {contenido}

    EJEMPLO DE RESPUESTA CORRECTA (NO copies, úsalo como referencia):
    Input: "La UAGRM habilitará retiro próxima semana"
    Output JSON:
    {{
      "text": "🚨 ¡ATENCIÓN FICCT! 🚨\\n\\nLa UAGRM acaba de confirmar que el retiro académico estará HABILITADO la próxima semana ⏰\\n\\nSi estás evaluando tu carga académica, este anuncio te interesa 👀📚\\n\\n#UAGRM #FICCT #EstudiantesUAGRM #UniversidadBo #InfoAcadémica #ComunidadUAGRM #Actualización",
      "tts_text": "Atención estudiantes de la Facultad de Ingeniería de Ciencias de la Computación. La próxima semana se habilitarán las inscripciones de materias.",
      "hashtags": ["#UAGRM", "#FICCT", "#EstudiantesUAGRM", "#UniversidadBo", "#InfoAcadémica", "#ComunidadUAGRM", "#Actualización"],
      "character_count": 238,
      "video_hook": "La Universidad Autónoma Gabriel René Moreno confirma el retiro académico para la próxima semana."
    }}

    Debes devolver EXACTAMENTE un JSON válido con esta estructura:
    {{
      "text": "Texto COMPLETO y COHERENTE con emojis, saltos de línea (\\n), y hashtags INCLUIDOS",
      "tts_text": "Texto donde FICCT se dice 'Facultad de Ingeniería de Ciencias de la Computación' y UAGRM se dice 'Universidad Autónoma Gabriel René Moreno'. SIN emojis, SIN hashtags, SIN frases informales como 'Participa y comparte tu opinión'.",
      "hashtags": ["#UAGRM", "#Facultad", "#Tema", "#EstudiantesUAGRM"],
      "character_count": número,
      "video_hook": "Primera frase impactante (también reemplazando FICCT y UAGRM por nombres completos)"
    }}

    IMPORTANTE:
    - El "text" ya debe INCLUIR los hashtags al final (para mostrar en pantalla)
    - El "tts_text" DEBE reemplazar: FICCT → "Facultad de Ingeniería de Ciencias de la Computación", UAGRM → "Universidad Autónoma Gabriel René Moreno"
    - El "video_hook" también debe usar nombres completos (es para audio)
    - NO uses frases informales en tts_text
    - Usa \\n para saltos de línea legibles
    - Cada línea del texto debe tener propósito
    """,
    "whatsapp": """
    Eres un experto en comunicación directa especializado en WhatsApp para instituciones académicas.
    Tu tarea es adaptar contenido académico/universitario para ser enviado por este canal.

    Características de WhatsApp para instituciones académicas:
    - Tono: Directo, conversacional, cercano y amigable.
    - Formato: Texto libre con saltos de línea para facilitar la lectura.
    - Hashtags: Raros o ninguno (WhatsApp no usa hashtags).
    - Emojis: Sí, como en una conversación normal (📚 ✅ 📅 👋 📢).
    - Enfoque: Mensaje personal y directo, como si hablaras con un estudiante.
    - Estructura: Saludo → Información → Despedida/Call to action

    Contenido a adaptar:
    - Título: {titulo}
    - Contenido: {contenido}

    Debes devolver un JSON con la siguiente estructura exacta:
    {{
      "text": "Hola! 👋\n\nTe cuento que...\n\nSi tienes dudas, escríbenos!",
      "hashtags": [],
      "character_count": 123,
      "format": "conversational",
      "suggested_image_prompt": "Un prompt de imagen simple y claro para WhatsApp"
    }}

    IMPORTANTE: 
    - Usa saltos de línea (\\n) para organizar el mensaje
    - Mantén un tono amigable pero profesional
    - Incluye emojis moderadamente
    - NO uses hashtags
    """
}


import json
import httpx

def validar_contenido_academico(texto: str) -> dict:
    """
    Valida si el contenido es apropiado para publicación académica/universitaria.
    VERSIÓN MEJORADA: Acepta contenido relacionado con UAGRM incluso si es sensible.
    """
    prompt_validacion = f"""
    Eres un moderador de contenido para redes sociales de la UAGRM (Universidad Autónoma Gabriel René Moreno).
    Tu tarea es determinar si el siguiente contenido es apropiado para publicar en las redes sociales oficiales de la universidad.
    
    ⭐ REGLA CRÍTICA: Si el contenido menciona "UAGRM" o cualquiera de sus facultades (FICCT, FIA, FCS, FACICO, Medicina, Derecho, Economía, etc.), 
    el contenido DEBE ser considerado académico, ya que se refiere directamente a la institución universitaria.
    
    Contenido APROPIADO y VÁLIDO para publicación:
    ✅ Cualquier tema que mencione UAGRM o sus facultades
    ✅ Fechas académicas (inscripciones, retiros, exámenes, defensa de tesis)
    ✅ Eventos académicos (conferencias, seminarios, talleres, congresos, ferias)
    ✅ Convocatorias (becas, programas, concursos académicos, contrataciones docentes)
    ✅ Logros estudiantiles, de investigación o institucionales
    ✅ Información sobre carreras, programas académicos, nuevas ofertas
    ✅ Actividades culturales, deportivas o sociales universitarias
    ✅ Noticias institucionales de la universidad
    ✅ Denuncias, conflictos o temas sensibles RELACIONADOS con la UAGRM o su comunidad
    ✅ Comunicados oficiales, pronunciamientos institucionales
    ✅ Procesos administrativos universitarios
    ✅ Huelgas, protestas, manifestaciones estudiantiles o docentes
    ✅ Problemas de infraestructura, presupuesto, gestión universitaria
    ✅ Casos de acoso, discriminación, injusticias en el campus
    
    Contenido NO apropiado (solo si NO está relacionado con UAGRM):
    ❌ Noticias de crimen o violencia que no involucran a la universidad
    ❌ Chismes de famosos o contenido de espectáculos sin relación académica
    ❌ Promociones comerciales externas sin vínculo educativo
    ❌ Contenido político partidista ajeno a la universidad
    ❌ Temas completamente ajenos a educación y universidad
    
    IMPORTANTE: 
    - Los temas sensibles (denuncias, conflictos laborales, protestas estudiantiles) son VÁLIDOS si están relacionados con UAGRM
    - La universidad puede y debe comunicar tanto logros como problemas institucionales
    - NO rechaces contenido solo porque sea controversial o sensible si es relevante para la comunidad universitaria
    - Si el texto menciona "docentes de la Universidad", "estudiantes de UAGRM", "FICCT", etc., ES CONTENIDO ACADÉMICO VÁLIDO
    
    Contenido a evaluar: "{texto}"
    
    Debes responder ÚNICAMENTE con un JSON en el siguiente formato:
    {{
      "es_academico": true o false,
      "razon": "Breve explicación de por qué es o no académico"
    }}7
    
    NO incluyas texto adicional, SOLO el JSON.
    """
    
    try:
        response = model.generate_content(prompt_validacion)
        response_text = response.text.strip()
        
        # Limpiar markdown si existe
        response_text = response_text.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        resultado = json.loads(response_text)
        return resultado
        
    except Exception as e:
        print(f"Error al validar contenido académico: {e}")
        # En caso de error, permitimos el contenido (fail-safe)
        return {
            "es_academico": True,
            "razon": "Error en validación, se permite por defecto"
        }


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
        
        # 4. Parsear la respuesta
        response_text = response.text.strip()
        
        # Limpiar markdown si existe
        response_text = response_text.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        # Parsear JSON
        response_json = json.loads(response_text)
        
        # 5. Si la respuesta es una lista, tomar el primer elemento
        if isinstance(response_json, list):
            if len(response_json) > 0:
                response_json = response_json[0]
            else:
                return {"error": "Respuesta vacía del LLM"}
        
        # 6. Verificar que sea un diccionario válido
        if not isinstance(response_json, dict):
            return {"error": f"Formato de respuesta inválido: {type(response_json)}"}
        
        return response_json
        
    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON de Gemini para {red_social}: {e}")
        print(f"Respuesta recibida: {response.text[:200]}")
        return {"error": f"Error al parsear respuesta JSON: {str(e)}"}
    except Exception as e:
        print(f"Error al llamar a Gemini para {red_social}: {e}")
        return {"error": f"Error al generar contenido para {red_social}."}


# ============================================
# 🆕 GENERACIÓN DE IMÁGENES CON REPLICATE
# ============================================

def generar_imagen_ia(prompt_imagen: str) -> str:
    """
    Genera imagen con IA y sube a Imgur
    """
    try:
        import httpx
        import base64
        
        STABILITY_KEY = os.getenv("STABILITY_API_KEY")
        
        print(f"🎨 Generando con Stability AI...")
        print(f"📝 Prompt: {prompt_imagen[:100]}...")
        
        response = httpx.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            headers={
                "Authorization": f"Bearer {STABILITY_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "text_prompts": [{"text": f"professional university photo, {prompt_imagen}, realistic, high quality"}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
            },
            timeout=60.0
        )
        response.raise_for_status()
        
        result = response.json()
        imagen_base64_str = result["artifacts"][0]["base64"]
        imagen_bytes = base64.b64decode(imagen_base64_str)
        
        print(f"✅ Imagen generada ({len(imagen_bytes)} bytes)")
        
        # Subir a Imgur
        print("📤 Subiendo a Imgur...")
        imgur_response = httpx.post(
            "https://api.imgur.com/3/upload",
            headers={"Authorization": "Client-ID 546c25a59c58ad7"},
            files={"image": imagen_bytes},
            timeout=30.0
        )
        imgur_response.raise_for_status()
        
        url_imgur = imgur_response.json()["data"]["link"]
        print(f"✅ Imgur: {url_imgur}")
        return url_imgur
            
    except Exception as e:
        print(f"❌ Error con IA: {e}")
        # Fallback a imagen estática que funciona
        print("⚠️ Usando imagen de respaldo...")
        
        response = httpx.get("https://picsum.photos/id/180/1080/1080", follow_redirects=True)
        imagen_bytes = response.content
        
        imgur_response = httpx.post(
            "https://api.imgur.com/3/upload",
            headers={"Authorization": "Client-ID 546c25a59c58ad7"},
            files={"image": imagen_bytes}
        )
        return imgur_response.json()["data"]["link"]


def generar_imagen_ia_base64(prompt_imagen: str) -> str:
    try:
        import httpx
        import base64
        
        STABILITY_KEY = os.getenv("STABILITY_API_KEY")
        
        if not STABILITY_KEY:
            return "https://picsum.photos/800/800"
        
        print(f"🎨 Generando con Stability AI (base64)...")
        
        response = httpx.post(
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
            
            headers={
                "Authorization": f"Bearer {STABILITY_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "text_prompts": [{"text": f"professional photo, {prompt_imagen}, university, realistic"}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
            },
            timeout=60.0
        )
        
        result = response.json()
        imagen_base64_str = result["artifacts"][0]["base64"]
        
        # Convertir a data URL
        data_url = f"data:image/png;base64,{imagen_base64_str}"
        
        print(f"✅ Imagen generada en base64")
        return data_url
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return "https://picsum.photos/800/800"


def extraer_keywords_con_llm(texto: str) -> list:
    """
    🆕 SISTEMA PROFESIONAL: Analiza el contenido y genera keywords contextuales
    
    Estrategia:
    1. Identifica el tema principal (evento, fecha académica, tecnología, etc.)
    2. Extrae entidades clave (FICCT, UAGRM, nombres de eventos)
    3. Genera keywords visuales específicas para Pexels
    4. Valida y enriquece con contexto universitario
    """
    prompt_keywords = f"""
    Eres un experto en búsqueda de videos de stock para contenido universitario.
    
    Tu tarea es analizar el siguiente texto académico y generar 3 keywords PERFECTAS 
    para encontrar videos relevantes en Pexels (banco de videos stock).
    
    ANÁLISIS REQUERIDO:
    1. Identifica el TEMA PRINCIPAL (evento, actividad, fecha académica, tecnología, etc.)
    2. Detecta ENTIDADES CLAVE (FICCT, UAGRM, facultades, carreras, nombres propios)
    3. Extrae CONCEPTOS VISUALES (¿qué se vería en un video sobre esto?)
    4. Considera el CONTEXTO GEOGRÁFICO (Bolivia, América Latina, universidad local)
    
    REGLAS PARA KEYWORDS (CRÍTICO):
    ✅ Cada keyword debe tener 3-5 palabras en INGLÉS
    ✅ GENERALMENTE incluir "university" o "college" o "campus" para dar contexto
    ✅ EXCEPCIÓN: Para eventos visuales fuertes (Navidad, Halloween, Fiestas, Deportes), PRIORIZA la acción y las personas sobre el lugar.
       - BIEN: "group of friends celebrating christmas party"
       - MAL: "christmas university campus empty"
    ✅ Ser ESPECÍFICO al tema: no genérico
    ✅ Describir lo VISUAL: ¿qué se vería en el video?
    ✅ Usar términos que existan en videos de stock (profesionales, reales)
    
    MAPEO TEMÁTICO (Úsalo como referencia):
    
    📅 FECHAS ACADÉMICAS:
    - Inscripciones → "university registration desk students", "college enrollment office line", "campus admission process"
    - Retiros → "students consulting academic advisor", "university office meeting", "campus administrative building"
    - Exámenes → "students studying library books", "university exam preparation classroom", "college finals week stress"
    - Inicio de clases → "university students walking campus", "college classroom first day", "campus backpacks students"
    
    🎓 FACULTADES/CARRERAS:
    - FICCT/Computación → "computer science students coding", "IT university lab programming", "software engineering classroom"
    - Ingeniería → "engineering students laboratory", "technical university workshop", "campus engineering building"
    - Medicina → "medical students anatomy class", "university hospital training", "healthcare education campus"
    - Derecho → "law students library books", "university legal education", "campus law school building"
    
    🎉 EVENTOS (PRIORIZAR PERSONAS Y CELEBRACIÓN):
    - Navidad/Festividades → "group of friends celebrating christmas party", "people wearing santa hats having fun", "happy students holding sparklers holiday"
    - Graduación → "university graduation ceremony caps", "college commencement celebration", "happy graduates throwing hats"
    - Conferencias → "university conference auditorium speaker", "academic seminar students listening", "campus lecture hall presentation"
    - Ferias → "university career fair booths", "college expo students networking", "campus event tents crowds"
    
    💻 TECNOLOGÍA/INVESTIGACIÓN:
    - IA/Machine Learning → "artificial intelligence university research", "computer science AI laboratory", "technology students coding projects"
    - Robótica → "robotics university engineering lab", "students building robot campus", "technology competition university"
    - Investigación → "university research laboratory scientists", "academic study campus library", "students experiment science lab"
    
    🏆 LOGROS/COMPETENCIAS:
    - Premios → "university award ceremony students", "academic achievement celebration campus", "student competition winners trophy"
    - Hackatones → "hackathon university students coding", "programming competition campus", "tech event students laptops"
    - Deportes → "university sports team campus", "college athletic competition", "campus stadium students playing"
    
    📢 COMUNICADOS/NOTICIAS:
    - Anuncios importantes → "university announcement students gathering", "campus news board students reading", "college administration building"
    - Cambios administrativos → "university office meeting professional", "campus administrative staff", "college leadership building"
    - Protestas/Huelgas → "student protest university campus", "college demonstration peaceful", "campus activism students signs"
    
    ❌ NUNCA GENERES:
    - Keywords de 1-2 palabras: "students", "university", "christmas"
    - Keywords abstractas: "education", "learning", "knowledge"
    - Keywords sin contexto universitario (SALVO EVENTOS): "people walking", "building exterior"
    - Keywords muy específicas que no existan en stock: "UAGRM building", "FICCT logo"
    
    ✅ SIEMPRE GENERA:
    - Keywords de 3-5 palabras con contexto claro
    - Términos visuales y concretos
    - Combinaciones que existan en videos profesionales de stock
    - Vocabulario internacional (Latin America, Bolivia si es relevante)
    
    TEXTO A ANALIZAR:
    "{texto}"
    
    RESPONDE ÚNICAMENTE CON ESTE JSON (sin markdown, sin comas finales, sin truncar):
    {{
      "tema_principal": "Breve descripción del tema",
      "entidades_clave": ["FICCT", "UAGRM"],
      "conceptos_visuales": ["concepto1", "concepto2", "concepto3"],
      "keywords": [
        "keyword específica 1 (3-5 palabras en inglés)",
        "keyword específica 2 (3-5 palabras en inglés)",
        "keyword específica 3 (3-5 palabras en inglés)"
      ],
      "razon": "Por qué elegiste estas keywords"
    }}
    
    IMPORTANTE:
    - NO uses comas después del último elemento de arrays
    - Cierra TODOS los corchetes y llaves
    - NO truncues el JSON
    """
    
    try:
        print("🔍 Analizando contenido para extraer keywords profesionales...")
        response = model.generate_content(prompt_keywords)
        response_text = response.text.strip()
        
        # Limpiar markdown
        response_text = response_text.replace('```json\n', '').replace('```json', '').replace('```\n', '').replace('```', '').strip()
        
        # ✅ Limpiar trailing commas (comas finales)
        import re
        response_text = re.sub(r',(\s*[}\]])', r'\1', response_text)
        
        # ✅ Completar JSON truncado
        if not response_text.endswith('}'):
            # Si está cortado en keywords
            if '"keywords"' in response_text and not ']' in response_text.split('"keywords"')[-1]:
                response_text += '"],"razon":"JSON completado automáticamente"}'
            # Si está cortado en razon
            elif '"razon"' in response_text:
                response_text += '"}'
            else:
                response_text += '}'
        
        resultado = json.loads(response_text)
        
        keywords = resultado.get("keywords", [])
        tema = resultado.get("tema_principal", "")
        razon = resultado.get("razon", "")
        
        print(f"📊 Tema identificado: {tema}")
        print(f"🎯 Keywords generadas: {keywords}")
        print(f"💡 Razón: {razon}")
        
        # VALIDACIÓN Y ENRIQUECIMIENTO
        keywords_validadas = []
        
        # Palabras que indican evento fuerte y permiten omitir "university"
        STRONG_THEMES = ['christmas', 'holiday', 'party', 'celebration', 'halloween', 'festival', 'concert', 'sport', 'game']
        
        for kw in keywords[:3]:
            palabras = kw.split()
            kw_lower = kw.lower()
            
            # Validar longitud mínima
            if len(palabras) < 3:
                print(f"⚠️ Keyword muy corta: '{kw}', enriqueciendo...")
                # Agregar contexto universitario
                if "university" not in kw_lower and "college" not in kw_lower and "campus" not in kw_lower:
                    kw = f"{kw} university campus"
                else:
                    kw = f"{kw} students"
            
            # Validar contexto universitario (CON EXCEPCIONES)
            tiene_contexto = any(word in kw_lower for word in ['university', 'college', 'campus', 'academic', 'student', 'class', 'school'])
            es_tema_fuerte = any(theme in kw_lower for theme in STRONG_THEMES)
            
            if not tiene_contexto and not es_tema_fuerte:
                print(f"⚠️ Keyword sin contexto universitario: '{kw}', agregando...")
                kw = f"{kw} university"
            elif es_tema_fuerte and not tiene_contexto:
                 print(f"ℹ️ Keyword de tema fuerte aceptada sin contexto explícito: '{kw}'")
            
            keywords_validadas.append(kw)
        
        # Si no se generaron suficientes keywords, usar fallback contextual
        if len(keywords_validadas) < 2:
            print("⚠️ Pocas keywords generadas, usando fallback contextual...")
            keywords_validadas = generar_keywords_fallback(texto)
        
        print(f"✅ Keywords finales validadas: {keywords_validadas}")
        
        return keywords_validadas[:3]
        
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON: {e}")
        print(f"Respuesta recibida: {response.text[:300]}")
        return generar_keywords_fallback(texto)
    except Exception as e:
        print(f"❌ Error extrayendo keywords: {e}")
        return generar_keywords_fallback(texto)


def generar_keywords_fallback(texto: str) -> list:
    """
    🆕 Sistema de fallback inteligente cuando falla el LLM
    
    Analiza el texto con reglas heurísticas para generar keywords contextuales
    """
    texto_lower = texto.lower()
    keywords_fallback = []
    
    # Detectar tema por palabras clave
    if any(word in texto_lower for word in ['inscripción', 'inscripciones', 'matrícula', 'registro']):
        keywords_fallback = [
            "university registration desk students",
            "college enrollment office line",
            "campus admission process"
        ]
    
    elif any(word in texto_lower for word in ['retiro', 'retiros', 'abandono']):
        keywords_fallback = [
            "students consulting academic advisor",
            "university office meeting",
            "campus administrative process"
        ]
    
    elif any(word in texto_lower for word in ['examen', 'exámenes', 'prueba', 'evaluación']):
        keywords_fallback = [
            "students studying library books",
            "university exam preparation classroom",
            "college finals week campus"
        ]
    
    elif any(word in texto_lower for word in ['navidad', 'christmas', 'festivo', 'celebración', 'fiesta']):
        keywords_fallback = [
             "group of friends celebrating christmas party",  # Gente celebrando
             "people wearing santa hats having fun",  # Gorros navideños y diversión
             "happy students holding sparklers holiday" # Estudiantes con luces
        ]
    
    elif any(word in texto_lower for word in ['graduación', 'titulación', 'grado']):
        keywords_fallback = [
            "university graduation ceremony caps",
            "college commencement celebration",
            "campus graduation students families"
        ]
    
    elif any(word in texto_lower for word in ['ficct', 'computación', 'sistemas', 'informática', 'programación']):
        keywords_fallback = [
            "computer science students coding",
            "IT university lab programming",
            "software engineering classroom"
        ]
    
    elif any(word in texto_lower for word in ['conferencia', 'seminario', 'charla', 'ponencia']):
        keywords_fallback = [
            "university conference auditorium speaker",
            "academic seminar students listening",
            "campus lecture hall presentation"
        ]
    
    elif any(word in texto_lower for word in ['feria', 'expo', 'exposición']):
        keywords_fallback = [
            "university career fair booths",
            "college expo students networking",
            "campus event tents crowds"
        ]
    
    elif any(word in texto_lower for word in ['investigación', 'research', 'estudio', 'proyecto']):
        keywords_fallback = [
            "university research laboratory scientists",
            "academic study campus library",
            "students experiment science lab"
        ]
    
    elif any(word in texto_lower for word in ['huelga', 'protesta', 'manifestación', 'paro']):
        keywords_fallback = [
            "student protest university campus",
            "college demonstration peaceful",
            "campus activism students gathering"
        ]
    
    elif any(word in texto_lower for word in ['ia', 'inteligencia artificial', 'machine learning', 'ai']):
        keywords_fallback = [
            "artificial intelligence university research",
            "computer science AI laboratory",
            "technology students coding projects"
        ]
    
    else:
        # Fallback genérico pero contextual
        keywords_fallback = [
            "university campus students walking",
            "college classroom learning activity",
            "academic campus buildings exterior"
        ]
    
    print(f"🔄 Usando keywords fallback: {keywords_fallback}")
    return keywords_fallback

def buscar_video_pexels_inteligente(keywords: list, orientation: str = "portrait") -> list:
    """
    🆕 Busca videos en Pexels con estrategia de fallback y VALIDACIÓN ESTRICTA
    
    Mejoras:
    1. Valida que keywords tengan mínimo 3 palabras
    2. Intenta keyword completa → simplificada → primera palabra
    3. Fallback inteligente si no encuentra suficientes
    4. Evita videos irrelevantes con filtros de calidad
    
    Args:
        keywords: Lista de keywords específicas (mínimo 3 palabras cada una)
        orientation: "portrait" para TikTok
    
    Returns:
        Lista de URLs de videos encontrados (mínimo 2, máximo 3)
    """
    video_urls = []
    
    # ═══════════════════════════════════════════════════════════════
    # 🔍 VALIDACIÓN CRÍTICA: Keywords deben ser específicas
    # ═══════════════════════════════════════════════════════════════
    keywords_validas = []
    
    for kw in keywords[:3]:  # Máximo 3 keywords
        palabras = kw.split()
        
        if len(palabras) >= 3:
            keywords_validas.append(kw)
            print(f"✅ Keyword válida: '{kw}' ({len(palabras)} palabras)")
        else:
            print(f"⚠️ Keyword muy corta: '{kw}' ({len(palabras)} palabras) - RECHAZADA")
    
    # Si no hay keywords válidas, usar fallback genérico pero específico
    if not keywords_validas:
        print("❌ Ninguna keyword válida detectada")
        print("🔄 Usando keywords de respaldo profesionales...")
        keywords_validas = [
            "university campus students walking daytime",
            "college building exterior establishing shot wide",
            "academic institution students studying library"
        ]
    
    print(f"\n🔍 Keywords finales para búsqueda: {keywords_validas}\n")
    
    # ═══════════════════════════════════════════════════════════════
    # 🎬 BÚSQUEDA CON ESTRATEGIA DE FALLBACK
    # ═══════════════════════════════════════════════════════════════
    
    for keyword in keywords_validas[:2]:  # Buscar con las 2 mejores keywords
        print(f"───────────────────────────────────────")
        print(f"🔍 Buscando: '{keyword}'")
        
        # ─────────────────────────────────────────────────────────
        # INTENTO 1: Keyword completa (3-5 palabras)
        # ─────────────────────────────────────────────────────────
        url = buscar_video_pexels(keyword, orientation)
        if url:
            video_urls.append(url)
            print(f"✅ Video encontrado con keyword completa")
            continue
        
        print(f"⚠️ No encontrado con keyword completa")
        
        # ─────────────────────────────────────────────────────────
        # INTENTO 2: Versión simplificada (primeras 3 palabras)
        # ─────────────────────────────────────────────────────────
        palabras = keyword.split()
        if len(palabras) > 3:
            keyword_simplificada = " ".join(palabras[:3])
            print(f"🔄 Intentando versión simplificada: '{keyword_simplificada}'")
            
            url = buscar_video_pexels(keyword_simplificada, orientation)
            if url:
                video_urls.append(url)
                print(f"✅ Video encontrado con versión simplificada")
                continue
            
            print(f"⚠️ No encontrado con versión simplificada")
        
        # ─────────────────────────────────────────────────────────
        # INTENTO 3: Primeras 2 palabras (más general)
        # ─────────────────────────────────────────────────────────
        if len(palabras) >= 2:
            keyword_base = " ".join(palabras[:2])
            print(f"🔄 Intentando versión base: '{keyword_base}'")
            
            url = buscar_video_pexels(keyword_base, orientation)
            if url:
                video_urls.append(url)
                print(f"✅ Video encontrado con versión base")
                continue
            
            print(f"⚠️ No encontrado con versión base")
        
        print(f"❌ No se encontró video para: '{keyword}'")
    
    # ═══════════════════════════════════════════════════════════════
    # 🆘 FALLBACK FINAL: Si no se encontraron suficientes videos
    # ═══════════════════════════════════════════════════════════════
    if len(video_urls) < 2:
        print("\n" + "═"*50)
        print("⚠️ INSUFICIENTES VIDEOS - ACTIVANDO FALLBACK")
        print("═"*50)
        
        fallback_keywords = [
            "university campus students walking",
            "college building exterior drone",
            "academic students classroom learning",
            "campus students studying library",
            "university hallway students walking"
        ]
        
        for fb_keyword in fallback_keywords:
            if len(video_urls) >= 3:
                break
            
            print(f"🔄 Fallback: '{fb_keyword}'")
            url = buscar_video_pexels(fb_keyword, orientation)
            
            if url and url not in video_urls:
                video_urls.append(url)
                print(f"✅ Video fallback agregado")
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 RESULTADO FINAL
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "═"*50)
    print(f"📊 RESULTADO: {len(video_urls)} videos encontrados")
    print("═"*50)
    
    if not video_urls:
        print("❌ No se encontraron videos (esto NO debería pasar)")
        # Último recurso: videos universitarios genéricos garantizados
        print("🆘 Usando videos de respaldo de emergencia...")
        video_urls = [
            "https://videos.pexels.com/video-files/3209828/3209828-uhd_2160_3840_25fps.mp4",  # Campus students
            "https://videos.pexels.com/video-files/5198252/5198252-uhd_2732_1440_25fps.mp4"   # University building
        ]
    
    return video_urls[:3]  # Máximo 3 videos      


def buscar_video_pexels(query: str, orientation: str = "portrait") -> str:
    """
    Busca un video en Pexels API
    """
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
    
    if not PEXELS_API_KEY:
        print("⚠️ PEXELS_API_KEY no configurada")
        return None
    
    headers = {"Authorization": PEXELS_API_KEY}
    
    params = {
        "query": query,
        "per_page": 1,
        "orientation": orientation,  # portrait para TikTok
        "size": "medium"
    }
    
    try:
        response = httpx.get(
            "https://api.pexels.com/videos/search",
            headers=headers,
            params=params,
            timeout=10.0
        )
        response.raise_for_status()
        
        data = response.json()
        videos = data.get("videos", [])
        
        if videos:
            # Buscar el archivo de video en resolución portrait
            video_files = videos[0].get("video_files", [])
            
            # Priorizar resolución HD portrait
            for vf in video_files:
                if vf.get("width", 0) < vf.get("height", 0):  # Portrait
                    print(f"✅ Video encontrado: {query}")
                    return vf.get("link")
            
            # Si no hay portrait, usar el primero
            if video_files:
                return video_files[0].get("link")
        
        print(f"⚠️ No se encontraron videos para: {query}")
        return None
        
    except Exception as e:
        print(f"❌ Error buscando video en Pexels: {e}")
        return None





def limpiar_texto_para_tts(texto: str) -> str:
    """
    Limpia el texto para que gTTS lo lea naturalmente.
    - Elimina emojis
    - Elimina hashtags
    - Elimina caracteres especiales
    - Reemplaza siglas por nombres completos (FICCT, UAGRM, etc.)
    - Mantiene solo el contenido hablable
    """
    import re
    
    # 1. Eliminar hashtags (#UAGRM, #FICCT, etc.)
    texto_limpio = re.sub(r'#\w+', '', texto)
    
    # 2. Eliminar emojis (todos los caracteres Unicode de emojis)
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        "]+", 
        flags=re.UNICODE
    )
    texto_limpio = emoji_pattern.sub('', texto_limpio)
    
    # 3. 🆕 Reemplazar siglas comunes por nombres completos
    reemplazos_siglas = {
        r'\bFICCT\b': 'Facultad de Ingeniería de Ciencias de la Computación',
        r'\bUAGRM\b': 'Universidad Autónoma Gabriel René Moreno',
        r'\bFIA\b': 'Facultad de Ingeniería Agrícola',
        r'\bFCS\b': 'Facultad de Ciencias de la Salud',
        r'\bFACICO\b': 'Facultad de Ciencias Económicas',
    }
    
    for sigla, nombre_completo in reemplazos_siglas.items():
        texto_limpio = re.sub(sigla, nombre_completo, texto_limpio, flags=re.IGNORECASE)
    
    # 4. Eliminar múltiples espacios y saltos de línea
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio)
    
    # 5. Eliminar símbolos repetidos (!!!, ???, etc.)
    texto_limpio = re.sub(r'([!?.])\1+', r'\1', texto_limpio)
    
    # 6. Limpiar espacios al inicio y final
    texto_limpio = texto_limpio.strip()
    
    print(f"📝 Texto original: {texto[:100]}...")
    print(f"🧹 Texto limpio: {texto_limpio[:100]}...")
    
    return texto_limpio

def generar_guion_narracion(texto_original: str) -> str:
    """
    Usa IA para generar un guión de narración natural y expresivo.
    
    El LLM convierte el texto en un guión que suena como si una persona
    real estuviera hablando, con pausas naturales, énfasis y fluidez.
    """
    
    prompt_narracion = f"""
    Eres un experto en locución y narración para videos de TikTok académicos.
    
    Tu tarea es convertir el siguiente texto académico en un GUIÓN DE NARRACIÓN
    natural, expresivo y conversacional para ser leído en voz alta.
    
    REGLAS PARA EL GUIÓN:
    ✅ Habla en segunda persona (tú) o primera persona del plural (nosotros)
    ✅ Usa un tono cercano, juvenil pero profesional
    ✅ Incluye pausas naturales usando comas (,) y puntos (.)
    ✅ Divide en frases cortas y fáciles de entender
    ✅ Agrega palabras de transición: "así que", "por eso", "recuerda que"
    ✅ Haz énfasis en lo importante usando mayúsculas ocasionales
    ✅ Termina con una pregunta o llamado a la acción
    ✅ Reemplaza "FICCT" con "Facultad de Ingeniería en Ciencias de la Computación"
    ✅ Reemplaza otras siglas por sus nombres completos cuando sea necesario
    ❌ NO uses palabras como "Oye", "Hey", "Hola" al inicio
    ❌ NO uses emojis, hashtags ni símbolos especiales
    ❌ NO leas literalmente el texto, REESCRÍBELO de forma conversacional
    ❌ NO menciones la sigla "FICCT" tal cual (di "la facultad" o su nombre completo)
    ❌ NO excedas 150 palabras (duración ideal: 10-15 segundos)
    
    Texto original: "{texto_original}"
    
    EJEMPLO DE BUENA NARRACIÓN:
    Input: "La UAGRM facultad FICCT habilitará retiro la próxima semana"
    Output: "Atención estudiantes de la Facultad de Ingeniería en Ciencias de la Computación. Tenemos 
    una noticia importante. La próxima semana ya puedes hacer el retiro de materias. 
    Así que, si estás pensando en retirarte de alguna materia, este es el momento. 
    No pierdas la oportunidad. Tienes toda la próxima semana para hacerlo. Comparte 
    esto con tus compañeros para que todos estén enterados."
    
    IMPORTANTE: Sé directo, ve al grano, sin saludos innecesarios.
    Responde SOLO con el guión de narración, sin explicaciones adicionales.
    El texto debe ser directo, natural y fácil de leer en voz alta.
    """
    
    try:
        print("🎬 Generando guión de narración con IA...")
        response = model.generate_content(prompt_narracion)
        guion = response.text.strip()
        
        # Limpiar markdown si existe
        guion = guion.replace('```', '').strip()
        
        print(f"✅ Guión generado: {guion[:100]}...")
        return guion
        
    except Exception as e:
        print(f"❌ Error generando guión: {e}")
        # Fallback: usar el texto original limpio
        return limpiar_texto_para_tts(texto_original)

def generar_audio_gTTS(texto: str, usar_guion_ia: bool = True) -> str:
    """
    Genera audio con Google TTS (gTTS) - VERSIÓN MEJORADA
    🆕 Ahora con velocidad x1.5
    """
    try:
        from gtts import gTTS
        from pydub import AudioSegment
        
        print(f"🎤 Generando audio con Google TTS (gTTS)...")
        
        # Generar guión inteligente con IA
        if usar_guion_ia:
            texto_final = generar_guion_narracion(texto)
        else:
            texto_final = limpiar_texto_para_tts(texto)
        
        if not texto_final or len(texto_final) < 10:
            print("⚠️ Texto demasiado corto, usando texto original")
            texto_final = texto
        
        print(f"📝 Texto que se leerá: {texto_final[:150]}...")
        
        # Crear audio con gTTS
        tts = gTTS(text=texto_final, lang='es', slow=False)
        
        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as audio_file:
            tts.save(audio_file.name)
            temp_audio_path = audio_file.name
        
        # 🆕 AUMENTAR VELOCIDAD x1.5 usando FFmpeg directamente
        print("⚡ Aumentando velocidad a x1.5 con FFmpeg...")
        
        # Crear ruta para audio acelerado
        audio_rapido_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
        
        # Usar FFmpeg para acelerar (atempo=1.5)
        subprocess.run([
            FFMPEG_PATH,
            '-i', temp_audio_path,
            '-filter:a', 'atempo=1.5',  # Acelerar 1.5x
            '-y',
            audio_rapido_path
        ], check=True, capture_output=True, text=True)
        
        # Limpiar audio temporal original
        os.unlink(temp_audio_path)
        
        print(f"✅ Audio generado con velocidad x1.5: {audio_rapido_path}")
        return audio_rapido_path
            
    except ImportError as e:
        print(f"❌ Librería faltante: {e}")
        print("💡 Instala: pip install gtts")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en FFmpeg al acelerar audio: {e.stderr if e.stderr else e}")
        # Si falla, devolver audio sin acelerar
        print("⚠️ Devolviendo audio sin acelerar")
        return temp_audio_path if 'temp_audio_path' in locals() else None
    except Exception as e:
        print(f"❌ Error generando audio: {e}")
        return None


def verificar_ffmpeg() -> bool:
    """
    Verifica si FFmpeg está instalado y disponible
    """
    try:
        result = subprocess.run(
            [FFMPEG_PATH, '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ FFmpeg verificado correctamente (versión encontrada)")
            return True
        else:
            print(f"⚠️ FFmpeg devolvió código: {result.returncode}")
            return False
    except FileNotFoundError:
        print(f"❌ FFmpeg NO encontrado en: {FFMPEG_PATH}")
        print("💡 Soluciones:")
        print(f"   1. Verifica que exista el archivo: {FFMPEG_PATH}")
        print(f"   2. O agrega FFmpeg al PATH de Windows")
        return False
    except Exception as e:
        print(f"❌ Error al verificar FFmpeg: {type(e).__name__}: {e}")
        return False


def combinar_videos_con_audio(video_urls: list, audio_path: str, duracion_total: int = 15) -> str:
    """
    Combina múltiples videos con audio usando FFmpeg
    🆕 Ahora ajusta duración automáticamente según el audio
    """
    try:
        # Verificar FFmpeg
        if not verificar_ffmpeg():
            return None

        print(f"🎬 Combinando {len(video_urls)} videos con audio...")

        # Descargar videos
        video_paths = []
        for i, url in enumerate(video_urls):
            if not url:
                continue

            print(f"📥 Descargando video {i+1}/{len(video_urls)}...")
            response = httpx.get(url, timeout=30.0)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as video_file:
                video_file.write(response.content)
                video_paths.append(video_file.name)

        if not video_paths:
            print("❌ No se descargaron videos")
            return None

        # 🆕 CALCULAR DURACIÓN DEL AUDIO
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        duracion_audio_segundos = len(audio) / 1000.0
        
        print(f"⏱️  Duración del audio: {duracion_audio_segundos:.1f} segundos")
        
        # Crear archivo temporal para el video final
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

        # Crear lista de archivos para FFmpeg
        concat_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        for path in video_paths:
            path_normalized = path.replace('\\', '/')
            concat_file.write(f"file '{path_normalized}'\n")
        concat_file.close()

        # Combinar videos
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

        print("🔄 Concatenando videos...")
        subprocess.run([
            FFMPEG_PATH, '-f', 'concat', '-safe', '0',
            '-i', concat_file.name,
            '-vf', f'scale=540:960:force_original_aspect_ratio=increase,crop=540:960',
            '-t', str(duracion_audio_segundos),  # 🆕 Usar duración del audio
            '-c:v', 'libx264', '-preset', 'ultrafast',
            '-y', temp_video
        ], check=True, capture_output=True, text=True)

        # Agregar audio
        print("🔄 Agregando audio...")
        subprocess.run([
            FFMPEG_PATH, '-i', temp_video, '-i', audio_path,
            '-c:v', 'copy', '-c:a', 'aac',
            '-map', '0:v:0', '-map', '1:a:0',
            '-shortest',
            '-y', output_path
        ], check=True, capture_output=True, text=True)

        print(f"✅ Video final creado: {output_path}")

        # Limpiar archivos temporales
        os.unlink(concat_file.name)
        os.unlink(temp_video)
        for path in video_paths:
            os.unlink(path)

        return output_path

    except Exception as e:
        print(f"❌ Error combinando videos: {type(e).__name__}: {e}")
        return None


def generar_video_tiktok(texto_adaptado: str, adaptacion: dict = None) -> str:
    """
    🎬 GENERACIÓN DE VIDEO TIKTOK - VERSIÓN PROFESIONAL
    
    Flujo completo:
    1. Extrae keywords contextuales con LLM mejorado
    2. Busca videos relevantes en Pexels con fallback inteligente
    3. Genera audio natural con gTTS (reemplazando siglas)
    4. Combina videos + audio con FFmpeg
    """
    print("\n" + "="*60)
    print("🎬 GENERANDO VIDEO PARA TIKTOK")
    print("="*60)
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 1: EXTRAER KEYWORDS PROFESIONALES
    # ═══════════════════════════════════════════════════════════════
    print("\n📝 [1/4] Analizando contenido...")
    keywords = extraer_keywords_con_llm(texto_adaptado)
    
    if not keywords:
        print("❌ No se pudieron generar keywords")
        return None
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 2: BUSCAR VIDEOS EN PEXELS
    # ═══════════════════════════════════════════════════════════════
    print("\n🔍 [2/4] Buscando videos en Pexels...")
    video_urls = buscar_video_pexels_inteligente(keywords)
    
    if not video_urls:
        print("❌ No se encontraron videos en Pexels")
        return None
    
    print(f"✅ Videos encontrados: {len(video_urls)}")
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 3: GENERAR AUDIO
    # ═══════════════════════════════════════════════════════════════
    print("\n🎤 [3/4] Generando audio...")
    
    if adaptacion and "tts_text" in adaptacion:
        texto_para_audio = adaptacion["tts_text"]
        print(f"✅ Usando tts_text del LLM: {texto_para_audio[:80]}...")
        audio_path = generar_audio_gTTS(texto_para_audio, usar_guion_ia=False)
    else:
        print(f"🎬 Generando guión de narración inteligente...")
        audio_path = generar_audio_gTTS(texto_adaptado, usar_guion_ia=True)
    
    if not audio_path:
        print("❌ No se pudo generar audio")
        return None
    
    print(f"✅ Audio generado: {audio_path}")
    
    # ═══════════════════════════════════════════════════════════════
    # PASO 4: COMBINAR VIDEOS + AUDIO
    # ═══════════════════════════════════════════════════════════════
    print("\n🎬 [4/4] Combinando videos con audio...")
    video_final = combinar_videos_con_audio(video_urls, audio_path)
    
    # Limpiar audio temporal
    if audio_path and os.path.exists(audio_path):
        os.unlink(audio_path)
    
    if video_final:
        print(f"\n🎉 VIDEO TIKTOK GENERADO EXITOSAMENTE")
        print(f"📁 Ruta: {video_final}")
        print("="*60 + "\n")
    else:
        print("❌ Error al combinar videos")
    
    return video_final
