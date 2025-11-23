import os
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
import tempfile
import re

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
import os

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
    Extrae 3 keywords principales del texto para buscar videos
    """
    prompt_keywords = f"""
    Del siguiente texto académico, extrae EXACTAMENTE 3 palabras clave en INGLÉS 
    para buscar videos de stock que representen visualmente el contenido.
    
    Las keywords deben ser:
    - Simples (1-2 palabras)
    - Generales (que existan videos en Pexels)
    - Relacionadas con educación universitaria
    
    Texto: "{texto}"
    
    Responde SOLO con un JSON:
    {{
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }}
    
    Ejemplos válidos:
    - ["students", "university", "studying"]
    - ["campus", "graduation", "books"]
    - ["classroom", "lecture", "college"]
    
    NO incluyas palabras muy específicas como nombres propios.
    """
    
    try:
        response = model.generate_content(prompt_keywords)
        response_text = response.text.strip()
        response_text = response_text.replace('```json\n', '').replace('```\n', '').replace('```', '').strip()
        
        resultado = json.loads(response_text)
        keywords = resultado.get("keywords", ["university", "students", "education"])
        
        print(f"🔍 Keywords extraídas: {keywords}")
        return keywords[:3]
        
    except Exception as e:
        print(f"⚠️ Error al extraer keywords: {e}")
        return ["university", "students", "education"]


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


def generar_audio_elevenlabs(texto: str) -> str:
    """
    Genera audio con Google TTS (gTTS) - VERSIÓN GRATUITA
    Reemplaza ElevenLabs para evitar costos
    """
    try:
        from gtts import gTTS
        
        print(f"🎤 Generando audio con Google TTS (gTTS)...")
        
        # Crear audio con gTTS
        tts = gTTS(text=texto, lang='es', slow=False)
        
        # Guardar en archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as audio_file:
            tts.save(audio_file.name)
            audio_path = audio_file.name
            print(f"✅ Audio generado: {audio_path}")
            return audio_path
            
    except ImportError:
        print("❌ gTTS no instalado. Ejecuta: pip install gtts")
        return None
    except Exception as e:
        print(f"❌ Error generando audio: {e}")
        return None


def verificar_ffmpeg() -> bool:
    """
    Verifica si FFmpeg está instalado y disponible en el sistema
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


def combinar_videos_con_audio(video_urls: list, audio_path: str, duracion_total: int = 15) -> str:
    """
    Combina múltiples videos con audio usando FFmpeg
    """
    try:
        # Verificar FFmpeg primero
        if not verificar_ffmpeg():
            print("❌ FFmpeg no está instalado o no está en el PATH")
            print("💡 Para instalar FFmpeg:")
            print("   Windows: Descarga desde https://www.gyan.dev/ffmpeg/builds/ y agrega al PATH")
            print("   Mac: brew install ffmpeg")
            print("   Linux: sudo apt install ffmpeg")
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
            # En Windows, escapar las barras invertidas en las rutas
            path_escaped = path.replace('\\', '/')
            concat_file.write(f"file '{path_escaped}'\n")
        concat_file.close()

        # Combinar videos
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name

        print("🔄 Paso 1: Concatenando videos...")
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_file.name,
            '-vf', f'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
            '-t', str(duracion_total),
            '-c:v', 'libx264', '-preset', 'fast',
            '-y', temp_video
        ], check=True, capture_output=True, text=True)

        # Agregar audio
        print("🔄 Paso 2: Agregando audio...")
        subprocess.run([
            'ffmpeg', '-i', temp_video, '-i', audio_path,
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
        print("❌ FFmpeg no encontrado. Por favor instala FFmpeg:")
        print("   Windows: https://www.gyan.dev/ffmpeg/builds/")
        print("   Mac: brew install ffmpeg")
        print("   Linux: sudo apt install ffmpeg")
        return None
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en FFmpeg: {e.stderr if e.stderr else e}")
        print(f"   Comando: {' '.join(e.cmd)}")
        return None
    except Exception as e:
        print(f"❌ Error combinando videos: {type(e).__name__}: {e}")
        return None


def generar_video_tiktok(texto_adaptado: str) -> str:
    """
    FUNCIÓN PRINCIPAL: Genera video completo para TikTok
    
    1. Extrae keywords del texto
    2. Busca videos en Pexels
    3. Genera audio con ElevenLabs
    4. Combina todo con FFmpeg
    
    Returns: Path del video final
    """
    print("\n" + "="*60)
    print("🎬 GENERANDO VIDEO PARA TIKTOK")
    print("="*60)
    
    # 1. Extraer keywords
    keywords = extraer_keywords_con_llm(texto_adaptado)
    
    # 2. Buscar videos
    video_urls = []
    for keyword in keywords:
        url = buscar_video_pexels(keyword)
        if url:
            video_urls.append(url)
    
    if not video_urls:
        print("❌ No se encontraron videos en Pexels")
        return None
    
    print(f"✅ Encontrados {len(video_urls)} videos")
    
    # 3. Generar audio
    audio_path = generar_audio_elevenlabs(texto_adaptado)
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