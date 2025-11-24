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
        print(f"✅ FFmpeg configurado correctamente: {FFMPEG_PATH}")
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
      "character_count": 123
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
      "format": "conversational"
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
    }}
    
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


def generar_imagen_ia(prompt_imagen: str) -> str:
    """
    Genera imagen y sube a Imgur - Para Instagram (necesita URL)
    """
    try:
        # 1. Generar imagen con Pollinations
        prompt_limpio = prompt_imagen[:300].replace(" ", "%20")
        url_pollinations = f"https://image.pollinations.ai/prompt/{prompt_limpio}?width=800&height=800&nologo=true"
        
        print(f"🎨 Generando imagen con Pollinations...")
        response = httpx.get(url_pollinations, timeout=30.0)
        response.raise_for_status()
        imagen_bytes = response.content
        print(f"✅ Imagen generada ({len(imagen_bytes)} bytes)")
        
        # 2. Subir a Imgur
        imgur_client_id = "546c25a59c58ad7"
        imgur_headers = {"Authorization": f"Client-ID {imgur_client_id}"}
        
        print("📤 Subiendo imagen a Imgur...")
        imgur_response = httpx.post(
            "https://api.imgur.com/3/upload",
            headers=imgur_headers,
            files={"image": imagen_bytes},
            timeout=30.0
        )
        imgur_response.raise_for_status()
        imgur_result = imgur_response.json()
        
        if imgur_result["success"]:
            url_imgur = imgur_result["data"]["link"]
            print(f"✅ Imagen subida a Imgur: {url_imgur}")
            return url_imgur
        else:
            return "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/University_Lecture_Hall.jpg/1200px-University_Lecture_Hall.jpg"
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/University_Lecture_Hall.jpg/1200px-University_Lecture_Hall.jpg"


def generar_imagen_ia_base64(prompt_imagen: str) -> str:
    """
    Genera imagen en base64 - Para WhatsApp Status
    """
    try:
        import base64
        
        prompt_limpio = prompt_imagen[:300].replace(" ", "%20")
        url_pollinations = f"https://image.pollinations.ai/prompt/{prompt_limpio}?width=800&height=800&nologo=true"
        
        print(f"🎨 Generando imagen...")
        response = httpx.get(url_pollinations, timeout=30.0)
        response.raise_for_status()
        imagen_bytes = response.content
        print(f"✅ Imagen generada ({len(imagen_bytes)} bytes)")
        
        # Convertir a base64
        imagen_base64 = base64.b64encode(imagen_bytes).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{imagen_base64}"
        print(f"✅ Convertida a base64")
        return data_url
        
    except Exception as e:
        print(f"❌ Error: {e}")
        prompt_limpio = prompt_imagen[:100].replace(" ", "%20")
        return f"https://image.pollinations.ai/prompt/{prompt_limpio}?width=800&height=800&nologo=true"


def extraer_keywords_con_llm(texto: str) -> list:
    """
    🆕 VERSIÓN MEJORADA: Extrae keywords ESPECÍFICAS para buscar videos relevantes
    
    Ahora analiza el contenido y genera keywords contextuales:
    - Si menciona FICCT/computación → "computer science", "programming", "coding"
    - Si menciona inscripciones → "registration desk", "students enrollment"
    - Si menciona exámenes → "students studying", "exam preparation"
    - Si menciona graduación → "graduation ceremony", "university caps"
    
    Genera 3-5 keywords en INGLÉS, específicas y visuales
    """
    prompt_keywords = f"""
    Eres un experto en selección de contenido visual para videos de TikTok académicos.
    
    Tu tarea es analizar el siguiente texto sobre la UAGRM (Universidad) y extraer 
    3-5 keywords en INGLÉS para buscar videos de stock que representen VISUALMENTE 
    y ESPECÍFICAMENTE el contenido.
    
    REGLAS CRÍTICAS:
    ✅ Las keywords deben ser ESPECÍFICAS al tema, no genéricas
    ✅ Piensa en qué se vería en el video, no solo el concepto
    ✅ Usa términos visuales y descriptivos
    ✅ SIEMPRE en INGLÉS (para Pexels API)
    ✅ Máximo 2-3 palabras por keyword
    ✅ Prioriza keywords que tengan alta probabilidad de tener videos
    
    CONTEXTO ACADÉMICO:
    - FICCT = Facultad de Ciencias de la Computación (computer science, IT, programming)
    - UAGRM = Universidad en Bolivia (university campus, college students)
    - Temas comunes: inscripciones, retiros, exámenes, clases, eventos
    
    EJEMPLOS DE KEYWORDS BUENAS vs MALAS:
    
    ❌ GENÉRICAS (EVITAR):
    - "students", "university", "college" (muy amplias)
    - "education", "learning" (muy abstractas)
    
    ✅ ESPECÍFICAS (USAR):
    - "computer science students", "programming classroom", "coding laptop"
    - "university registration desk", "students enrollment line"
    - "exam preparation library", "students studying laptop"
    - "graduation ceremony caps", "university campus entrance"
    - "classroom technology", "students presentation"
    
    ANÁLISIS POR TEMA:
    - Si habla de FICCT/computación → "computer lab", "coding students", "IT classroom"
    - Si habla de inscripciones → "registration desk", "students enrollment", "university admission"
    - Si habla de retiro de materias → "students consulting", "academic advising", "university office"
    - Si habla de exámenes → "students studying", "exam preparation", "library study"
    - Si habla de clases → "university lecture", "classroom students", "professor teaching"
    - Si habla de eventos → "university event", "students gathering", "campus activity"
    - Si habla de graduación → "graduation ceremony", "university caps", "diploma celebration"
    - Si habla de tecnología/IA → "artificial intelligence", "technology students", "computer science"
    
    Texto a analizar: "{texto}"
    
    Responde SOLO con un JSON:
    {{
      "keywords": ["keyword específica 1", "keyword específica 2", "keyword específica 3"],
      "razon": "Breve explicación de por qué elegiste estas keywords"
    }}
    
    IMPORTANTE: 
    - NO uses keywords genéricas como "students", "university" solas
    - SÍ combina palabras para ser específico: "computer science students"
    - Piensa: "¿Qué video de Pexels representaría mejor este tema?"
    """
    
    try:
        response = model.generate_content(prompt_keywords)
        response_text = response.text.strip()
        response_text = response_text.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        resultado = json.loads(response_text)
        keywords = resultado.get("keywords", ["university students", "college campus", "education"])
        razon = resultado.get("razon", "")
        
        print(f"🔍 Keywords extraídas: {keywords}")
        print(f"💡 Razón: {razon}")
        
        # Validar que no sean muy genéricas
        keywords_validadas = []
        for kw in keywords[:5]:  # Máximo 5
            # Si la keyword es muy corta (1 palabra), agregar contexto
            if len(kw.split()) == 1 and kw.lower() in ['students', 'university', 'college', 'education']:
                print(f"⚠️ Keyword muy genérica detectada: '{kw}', agregando contexto...")
                kw = f"{kw} campus"
            keywords_validadas.append(kw)
        
        return keywords_validadas[:5]
        
    except Exception as e:
        print(f"⚠️ Error al extraer keywords: {e}")
        # Fallback mejorado: keywords más específicas por defecto
        return ["university campus students", "college classroom technology", "academic study library"]

def buscar_video_pexels_inteligente(keywords: list, orientation: str = "portrait") -> list:
    """
    🆕 Busca videos en Pexels con estrategia de fallback
    
    1. Intenta buscar con keywords específicas
    2. Si no encuentra, usa versiones simplificadas
    3. Si aún no encuentra, usa keywords genéricas de respaldo
    
    Args:
        keywords: Lista de keywords específicas
        orientation: "portrait" para TikTok
    
    Returns:
        Lista de URLs de videos encontrados
    """
    video_urls = []
    
    
    for keyword in keywords[:2]:
        # Intento 1: Keyword completa
        url = buscar_video_pexels(keyword, orientation)
        if url:
            video_urls.append(url)
            print(f"✅ Video encontrado con: '{keyword}'")
            continue
        
        # Intento 2: Si tiene más de 2 palabras, probar con las primeras 2
        palabras = keyword.split()
        if len(palabras) > 2:
            keyword_simplificada = " ".join(palabras[:2])
            print(f"🔄 Intentando versión simplificada: '{keyword_simplificada}'")
            url = buscar_video_pexels(keyword_simplificada, orientation)
            if url:
                video_urls.append(url)
                print(f"✅ Video encontrado con versión simplificada")
                continue
        
        # Intento 3: Usar solo la primera palabra si es descriptiva
        if len(palabras) > 0 and palabras[0].lower() not in ['the', 'a', 'an']:
            primera_palabra = palabras[0]
            print(f"🔄 Intentando primera palabra: '{primera_palabra}'")
            url = buscar_video_pexels(primera_palabra, orientation)
            if url:
                video_urls.append(url)
                print(f"✅ Video encontrado con primera palabra")
                continue
        
        print(f"⚠️ No se encontró video para: '{keyword}'")
    
    # Fallback final: Si no encontró suficientes videos
    if len(video_urls) < 2:
        print("🔄 Aplicando fallback genérico...")
        fallback_keywords = ["university campus", "students classroom", "college education"]
        for fb_keyword in fallback_keywords:
            if len(video_urls) >= 3:
                break
            url = buscar_video_pexels(fb_keyword, orientation)
            if url and url not in video_urls:
                video_urls.append(url)
                print(f"✅ Video fallback agregado: '{fb_keyword}'")
    
    return video_urls        


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

def generar_audio_elevenlabs(texto: str, usar_guion_ia: bool = True) -> str:
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
    """
    try:
        # Verificar FFmpeg primero
        if not verificar_ffmpeg():
            return None

        print(f"🎬 Combinando {len(video_urls)} videos con audio...")

        # Descargar videos
        video_paths = []
        for i, url in enumerate(video_urls):
            if not url:
                continue

            print(f"📥 Descargando video {i+1}...")
            response = httpx.get(url, timeout=30.0)

            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as video_file:
                video_file.write(response.content)
                video_paths.append(video_file.name)

        if not video_paths:
            print("❌ No se descargaron videos")
            return None

        # Crear archivo temporal para el video final
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

        # Crear lista de archivos para FFmpeg
        concat_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
        for path in video_paths:
            # Normalizar rutas para FFmpeg
            path_normalized = path.replace('\\', '/')
            concat_file.write(f"file '{path_normalized}'\n")
        concat_file.close()

        # Combinar videos
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

        print("🔄 Paso 1: Concatenando videos...")
        subprocess.run([
            FFMPEG_PATH, '-f', 'concat', '-safe', '0',
            '-i', concat_file.name,
             # 🔥 CAMBIO: De 1080x1920 a 720x1280
             '-vf', f'scale=540:960:force_original_aspect_ratio=increase,crop=540:960',
              '-t', str(duracion_total),
              '-c:v', 'libx264', '-preset', 'ultrafast',  # <- También cambiar 'fast' a 'ultrafast'
              '-y', temp_video
            ], check=True, capture_output=True, text=True)

        # Agregar audio
        print("🔄 Paso 2: Agregando audio...")
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

    except FileNotFoundError:
        print(f"❌ FFmpeg no encontrado en: {FFMPEG_PATH}")
        print("💡 Asegúrate de que FFmpeg esté instalado correctamente")
        print(f"   Ruta configurada: {FFMPEG_PATH}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en FFmpeg: {e.stderr if e.stderr else e}")
        print(f"   Comando: {' '.join(e.cmd)}")
        return None
    except Exception as e:
        print(f"❌ Error combinando videos: {type(e).__name__}: {e}")
        return None


def generar_video_tiktok(texto_adaptado: str, adaptacion: dict = None) -> str:
    """
    FUNCIÓN PRINCIPAL: Genera video completo para TikTok
    
    🆕 MEJORAS FASE 1:
    - Keywords más inteligentes y específicas
    - Sistema de fallback para garantizar videos
    """
    print("\n" + "="*60)
    print("🎬 GENERANDO VIDEO PARA TIKTOK")
    print("="*60)
    
    # 1. Extraer keywords INTELIGENTES
    keywords = extraer_keywords_con_llm(texto_adaptado)
    
    # 2. Buscar videos con sistema inteligente
    print(f"\n🔍 Buscando videos con keywords específicas...")
    video_urls = buscar_video_pexels_inteligente(keywords)
    
    if not video_urls:
        print("❌ No se encontraron videos en Pexels")
        return None
    
    print(f"✅ Encontrados {len(video_urls)} videos")
    
    # 3. Generar audio
    if adaptacion and "tts_text" in adaptacion:
        texto_para_audio = adaptacion["tts_text"]
        print(f"✅ Usando tts_text del LLM: {texto_para_audio[:100]}...")
        audio_path = generar_audio_elevenlabs(texto_para_audio, usar_guion_ia=False)
    else:
        print(f"🎬 Generando guión de narración inteligente...")
        audio_path = generar_audio_elevenlabs(texto_adaptado, usar_guion_ia=True)
    
    if not audio_path:
        print("❌ No se pudo generar audio")
        return None
    
    # 4. Combinar todo
    video_final = combinar_videos_con_audio(video_urls, audio_path)
    
    # Limpiar audio temporal
    if audio_path and os.path.exists(audio_path):
        os.unlink(audio_path)
    
    if video_final:
        print(f"🎉 Video TikTok generado exitosamente")
        print("="*60 + "\n")
    
    return video_final