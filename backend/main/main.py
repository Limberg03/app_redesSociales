from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import social_services
import schemas
import llm_service
import os

from auth import auth_schemas, auth_service
from auth.database import get_db, init_db, engine
from auth.models import User
from typing import Optional
from dependencies import get_current_user

app = FastAPI()

# Crear tablas de chat
from chat import models as chat_models
chat_models.Base.metadata.create_all(bind=engine)

from chat import routes as chat_routes
app.include_router(chat_routes.router)

@app.on_event("startup")
def startup_event():
    init_db()
    print("🚀 Servidor iniciado con autenticación")

# ✅ CORS ACTUALIZADO PARA PRODUCCIÓN
# Obtener los orígenes permitidos desde variables de entorno
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")

# Si no hay ALLOWED_ORIGINS configurado, usar localhost por defecto
if not ALLOWED_ORIGINS[0]:
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

# Agregar el origen de Vercel si está configurado
FRONTEND_URL = os.getenv("FRONTEND_URL")
if FRONTEND_URL and FRONTEND_URL not in ALLOWED_ORIGINS:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

print(f"🔓 CORS habilitado para: {ALLOWED_ORIGINS}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ Solo orígenes específicos en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "API del Sistema Multi-Red Social funcionando",
        "version": "2.0",
        "status": "online"
    }


@app.post("/api/auth/register", response_model=auth_schemas.LoginResponse)
def register(user_data: auth_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario
    """
    try:
        # Crear usuario
        new_user = auth_service.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        
        # Crear token
        token = auth_service.create_access_token(new_user)
        
        # Respuesta
        return auth_schemas.LoginResponse(
            success=True,
            message="Usuario registrado exitosamente",
            token=auth_schemas.Token(
                access_token=token,
                token_type="bearer",
                user=auth_schemas.UserResponse.from_orm(new_user)
            )
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al registrar: {str(e)}")


@app.post("/api/auth/login", response_model=auth_schemas.LoginResponse)
def login(credentials: auth_schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Inicia sesión y retorna un token
    """
    # Autenticar usuario
    user = auth_service.authenticate_user(
        db=db,
        username=credentials.username,
        password=credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario o contraseña incorrectos"
        )
    
    # Crear token
    token = auth_service.create_access_token(user)
    
    return auth_schemas.LoginResponse(
        success=True,
        message="Login exitoso",
        token=auth_schemas.Token(
            access_token=token,
            token_type="bearer",
            user=auth_schemas.UserResponse.from_orm(user)
        )
    )


@app.post("/api/auth/logout")
def logout(authorization: Optional[str] = Header(None)):
    """
    Cierra sesión (invalida el token)
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="No autenticado")
    
    token = authorization.replace("Bearer ", "")
    auth_service.logout_user(token)
    
    return {"message": "Logout exitoso"}


@app.get("/api/auth/me", response_model=auth_schemas.UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Obtiene la información del usuario actual
    """
    return auth_schemas.UserResponse.from_orm(current_user)


@app.post("/api/posts/adapt")
def adapt_post_content(request: schemas.AdaptRequest, current_user: User = Depends(get_current_user) ):
    """
    Recibe un título, contenido y lista de redes,
    y devuelve las adaptaciones generadas por el LLM.
    """
    
    print(f"Recibida solicitud para adaptar: {request.titulo}")
    
    adaptaciones_finales = {}
    
    for red in request.target_networks:
        if red not in llm_service.PROMPTS_POR_RED:
            adaptaciones_finales[red] = {"error": f"Red '{red}' no soportada."}
            continue

        resultado = llm_service.adaptar_contenido(
            titulo=request.titulo,
            contenido=request.contenido,
            red_social=red
        )
        
        adaptaciones_finales[red] = resultado

    if not adaptaciones_finales:
        raise HTTPException(status_code=400, detail="No se especificaron redes válidas.")

    return schemas.AdaptResponse(data=adaptaciones_finales)


@app.post("/api/test/facebook")
def test_post_facebook(request: schemas.TestPostRequest, current_user: User = Depends(get_current_user)):
    """ 
    Endpoint para publicar en Facebook
    - VALIDACIÓN de contenido académico
    - ADAPTACIÓN automática
    - SOLO TEXTO (sin imagen)
    """
    
    print("🔍 Validando contenido académico...")
    validacion = llm_service.validar_contenido_academico(request.text)
    
    if not validacion.get("es_academico", False):
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "contenido_no_academico",
                "mensaje": "❌ Este contenido no es apropiado para publicación académica. Por favor, ingrese información relacionada con actividades universitarias, fechas académicas, eventos educativos, etc."
            }
        )
    
    print(f"✅ Contenido validado como académico: {validacion.get('razon')}")
    
    print("🔄 Adaptando contenido para Facebook...")
    adaptacion = llm_service.adaptar_contenido(
        titulo=request.text[:50],
        contenido=request.text,
        red_social="facebook"
    )
    
    if "error" in adaptacion:
        raise HTTPException(status_code=400, detail=adaptacion["error"])
    
    texto_adaptado = adaptacion.get("text", request.text)
    
    if "hashtags" in adaptacion and adaptacion["hashtags"]:
        hashtags_str = " ".join(adaptacion["hashtags"])
        texto_adaptado = f"{texto_adaptado}\n\n{hashtags_str}"
    
    print(f"✅ Texto adaptado: {texto_adaptado[:100]}...")
    
    result = social_services.post_to_facebook(
        text=texto_adaptado,
        image_url=None  # SIN IMAGEN
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 5. Construir link del post
    post_id = result.get("id") or result.get("post_id")
    link_facebook = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else None
    
    # 6. Devolver la validación, adaptación y resultado de la publicación
    return {
        "validacion": validacion,
        "adaptacion": adaptacion,
        "publicacion": {
            "id": post_id,
            "link": link_facebook,
            "raw": result
        },
        "mensaje": "✅ Contenido académico validado, adaptado y publicado en Facebook (solo texto)"
    }


@app.post("/api/test/instagram")
def test_post_instagram(request: schemas.TestPostRequest, current_user: User = Depends(get_current_user)):
    """ 
    Endpoint para publicar en Instagram
    - VALIDACIÓN de contenido académico
    - ADAPTACIÓN automática
    - GENERACIÓN DE IMAGEN con IA
    """
    
    # 1. VALIDAR que el contenido sea académico
    print("🔍 Validando contenido académico...")
    validacion = llm_service.validar_contenido_academico(request.text)
    
    if not validacion.get("es_academico", False):
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "contenido_no_academico",
                "mensaje": "❌ Este contenido no es apropiado para publicación académica. Por favor, ingrese información relacionada con actividades universitarias, fechas académicas, eventos educativos, etc."
            }
        )
    
    print(f"✅ Contenido validado como académico: {validacion.get('razon')}")
    
    # 2. Adaptar el contenido
    print("🔄 Adaptando contenido para Instagram...")
    adaptacion = llm_service.adaptar_contenido(
        titulo=request.text[:50],
        contenido=request.text,
        red_social="instagram"
    )
    
    if "error" in adaptacion:
        raise HTTPException(status_code=400, detail=adaptacion["error"])
    
    # 3. Preparar texto adaptado con hashtags
    texto_adaptado = adaptacion.get("text", request.text)
    
    if "hashtags" in adaptacion and adaptacion["hashtags"]:
        hashtags_str = " ".join(adaptacion["hashtags"])
        texto_adaptado = f"{texto_adaptado}\n\n{hashtags_str}"
    
    print(f"✅ Texto adaptado: {texto_adaptado[:100]}...")
    
    # 4. GENERAR IMAGEN con IA
    print("🎨 Generando imagen con IA...")
    prompt_imagen = adaptacion.get("suggested_image_prompt", f"Universidad UAGRM, tema académico: {request.text[:100]}")
    imagen_url = llm_service.generar_imagen_ia(prompt_imagen)
    print(f"✅ Imagen generada: {imagen_url[:100]}...")
    
    # 5. Publicar en Instagram (CON IMAGEN GENERADA)
    result = social_services.post_to_instagram(
        text=texto_adaptado,
        image_url=imagen_url
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 6. Usar el permalink real de Instagram
    media_id = result.get("id")
    permalink = result.get("permalink")  # Este es el link REAL
    
    return {
        "validacion": validacion,
        "adaptacion": adaptacion,
        "imagen_generada": {
            "url": imagen_url,
            "prompt": prompt_imagen
        },
        "publicacion": {
            "id": media_id,
            "link": permalink,  # Link real de Instagram
            "raw": result
        },
        "mensaje": "✅ Contenido académico validado, adaptado, imagen generada y publicado en Instagram"
    }


@app.post("/api/test/linkedin")
def test_post_linkedin(request: schemas.TestPostRequest, current_user: User = Depends(get_current_user)):
    """ 
    Endpoint para publicar en LinkedIn 
    - VALIDACIÓN de contenido académico
    - ADAPTACIÓN automática (Tono profesional, sin emojis excesivos)
    - SOLO TEXTO (formato artículo/post)
    """
    
    # 1. VALIDAR contenido académico
    print("🔍 [LinkedIn] Validando contenido académico...")
    validacion = llm_service.validar_contenido_academico(request.text)
    
    if not validacion.get("es_academico", False):
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "contenido_no_academico",
                "mensaje": "❌ Contenido no apto para LinkedIn académico. " + validacion.get('razon', '')
            }
        )
    
    # 2. ADAPTAR contenido (Usa el prompt específico de LinkedIn en llm_service)
    print("🔄 [LinkedIn] Adaptando contenido con tono profesional...")
    adaptacion = llm_service.adaptar_contenido(
        titulo=request.text[:50],
        contenido=request.text,
        red_social="linkedin"
    )
    
    if "error" in adaptacion:
        raise HTTPException(status_code=400, detail=adaptacion["error"])
    
    # 3. Preparar texto final
    texto_adaptado = adaptacion.get("text", request.text)
    hashtags = adaptacion.get("hashtags", [])
    
    # LinkedIn prefiere los hashtags abajo, separados
    if hashtags:
        hashtags_str = " ".join(hashtags)
        texto_adaptado = f"{texto_adaptado}\n\n{hashtags_str}"
    
    print(f"✅ Texto LinkedIn: {texto_adaptado[:50]}...")
    
    # 4. PUBLICAR
    result = social_services.post_to_linkedin(text=texto_adaptado)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 5. Obtener Link (LinkedIn devuelve un URN tipo urn:li:share:12345)
    post_urn = result.get("id", "") # ej: urn:li:share:7123456789
    post_id = post_urn.split(":")[-1] if ":" in post_urn else post_urn
    link_linkedin = f"https://www.linkedin.com/feed/update/{post_urn}" if post_urn else None

    return {
        "validacion": validacion,
        "adaptacion": adaptacion,
        "publicacion": {
            "id": post_id,
            "link": link_linkedin,
            "raw": result
        },
        "mensaje": "✅ Publicado en LinkedIn (Tono Profesional)"
    }


@app.post("/api/test/whatsapp")
def test_post_whatsapp_status(request: schemas.TestPostRequest, current_user: User = Depends(get_current_user)):
    """ 
    🆕 Endpoint para publicar ESTADO en WhatsApp usando Whapi.Cloud
    - VALIDACIÓN de contenido académico
    - ADAPTACIÓN automática (Tono conversacional)
    - GENERACIÓN DE IMAGEN con IA
    - PUBLICACIÓN EN ESTADO (Story)
    """
    
    # 1. VALIDAR contenido académico
    print("🔍 [WhatsApp Status] Validando contenido académico...")
    validacion = llm_service.validar_contenido_academico(request.text)
    
    if not validacion.get("es_academico", False):
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "contenido_no_academico",
                "mensaje": "❌ Contenido no apto para WhatsApp académico. " + validacion.get('razon', '')
            }
        )
    
    # 2. ADAPTAR contenido (Usa el prompt específico de WhatsApp en llm_service)
    print("🔄 [WhatsApp Status] Adaptando contenido para Estado...")
    adaptacion = llm_service.adaptar_contenido(
        titulo=request.text[:50],
        contenido=request.text,
        red_social="whatsapp"
    )
    
    if "error" in adaptacion:
        raise HTTPException(status_code=400, detail=adaptacion["error"])
    
    # 3. Preparar texto final (sin hashtags para WhatsApp Status)
    texto_adaptado = adaptacion.get("text", request.text)
    
    print(f"✅ Texto WhatsApp: {texto_adaptado[:100]}...")
    
    # 4. GENERAR IMAGEN con IA (para el estado)
    print("🎨 Generando imagen para el estado...")
    prompt_imagen = f"Universidad UAGRM, tema académico: {request.text[:100]}"
    imagen_url = llm_service.generar_imagen_ia_base64(prompt_imagen)
    print(f"✅ Imagen generada: {imagen_url[:100]}...")
    
    # 5. PUBLICAR EN ESTADO DE WHATSAPP
    result = social_services.post_whatsapp_status(
        text=texto_adaptado,
        image_url=imagen_url
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {
        "validacion": validacion,
        "adaptacion": adaptacion,
        "imagen_generada": {
            "url": imagen_url,
            "prompt": prompt_imagen
        },
        "publicacion": {
            "id": result.get("id"),
            "status": result.get("status"),
            "raw": result
        },
        "mensaje": "✅ Estado publicado en WhatsApp con imagen generada"
    }

@app.post("/api/test/tiktok")
def test_post_tiktok(request: schemas.TestPostRequest, current_user: User = Depends(get_current_user)):
    """ 
    Endpoint para publicar en TikTok (PRIVADO)
    🆕 Ahora usa tts_text para audio limpio sin emojis
    """
    
    # 1. VALIDAR contenido académico
    print("🔍 [TikTok] Validando contenido académico...")
    validacion = llm_service.validar_contenido_academico(request.text)
    
    if not validacion.get("es_academico", False):
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "contenido_no_academico",
                "mensaje": "❌ Contenido no apto para TikTok académico. " + validacion.get('razon', '')
            }
        )
    
    # 2. ADAPTAR contenido
    print("🔄 [TikTok] Adaptando contenido para TikTok...")
    adaptacion = llm_service.adaptar_contenido(
        titulo=request.text[:50],
        contenido=request.text,
        red_social="tiktok"
    )
    
    if "error" in adaptacion:
        raise HTTPException(status_code=400, detail=adaptacion["error"])
    
    # 3. Preparar texto adaptado
    texto_adaptado = adaptacion.get("text", request.text)    
    if "hashtags" in adaptacion and adaptacion["hashtags"]:
        hashtags_str = " ".join(adaptacion["hashtags"])
        # Solo agregar hashtags si no están ya en el texto
        if not any(tag in texto_adaptado for tag in adaptacion["hashtags"]):
            texto_adaptado = f"{texto_adaptado}\n\n{hashtags_str}"
    
    print(f"✅ Texto TikTok: {texto_adaptado[:100]}...")
    
    if "tts_text" in adaptacion:
        print(f"✅ Texto para audio (limpio): {adaptacion['tts_text'][:100]}...")
    
    # 4. GENERAR VIDEO con IA
    print("🎬 [TikTok] Generando video con IA...")
    # 🔥 CAMBIO: Pasar la adaptación completa para usar tts_text
    video_path = llm_service.generar_video_tiktok(texto_adaptado, adaptacion)

    if not video_path:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "video_generation_failed",
                "mensaje": "Error al generar video."
            }
        )
    
    print(f"✅ Video generado: {video_path}")
    
    # 5. PUBLICAR EN TIKTOK (PRIVADO)
    result = social_services.post_to_tiktok(
        text=texto_adaptado,
        video_path=video_path,
        privacy="SELF_ONLY"  # PRIVADO
    )
    
    # 6. Limpiar video temporal
    if video_path and os.path.exists(video_path):
        os.unlink(video_path)
    
    # 7. Verificar resultado
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    
    # 8. Respuesta exitosa
    return {
        "validacion": validacion,
        "adaptacion": adaptacion,
        "video_generado": {
            "mensaje": "Video generado con Pexels + gTTS",
            "audio_usado": "tts_text limpio (sin emojis)" if "tts_text" in adaptacion else "texto limpiado automáticamente"
        },
        "publicacion": result,
        "mensaje": "✅ Video generado y publicado en TikTok (privado)"
    }



@app.post("/api/posts/publish-multi", response_model=schemas.MultiNetworkPostResponse)
def publish_to_multiple_networks(request: schemas.MultiNetworkPostRequest, current_user: User = Depends(get_current_user)):
    """
    🆕 ENDPOINT PRINCIPAL: Publica en múltiples redes sociales simultáneamente
    
    Flujo:
    1. Valida que el contenido sea académico
    2. Adapta el contenido para cada red social seleccionada
    3. Genera recursos necesarios (imágenes, videos)
    4. Publica en cada red
    5. Retorna resumen de publicaciones exitosas/fallidas
    
    Redes soportadas:
    - facebook (solo texto)
    - instagram (texto + imagen generada)
    - linkedin (texto profesional)
    - whatsapp (estado con imagen)
    - tiktok (video generado con IA)
    
    Ejemplo de uso:
    ```json
    {
        "text": "La FICCT anuncia retorno a clases presenciales este miércoles",
        "target_networks": ["facebook", "instagram", "tiktok"]
    }
    ```
    """
    import time
    
    inicio = time.time()
    
    print("\n" + "="*70)
    print("🚀 PUBLICACIÓN MULTI-RED INICIADA")
    print("="*70)
    print(f"📝 Contenido: {request.text[:80]}...")
    print(f"🎯 Redes objetivo: {', '.join(request.target_networks)}")
    print("="*70 + "\n")
    
    # ═══════════════════════════════════════════════════════════════
    # 🔍 PASO 1: VALIDAR CONTENIDO ACADÉMICO (una sola vez)
    # ═══════════════════════════════════════════════════════════════
    print("🔍 [PASO 1/5] Validando contenido académico...")
    validacion = llm_service.validar_contenido_academico(request.text)
    
    if not validacion.get("es_academico", False):
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "contenido_no_academico",
                "mensaje": "❌ Este contenido no es apropiado para publicación académica.",
                "razon": validacion.get('razon', ''),
                "redes_solicitadas": request.target_networks
            }
        )
    
    print(f"✅ Contenido validado: {validacion.get('razon')}\n")
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 PASO 2: ADAPTAR CONTENIDO PARA CADA RED (en paralelo)
    # ═══════════════════════════════════════════════════════════════
    print("🔄 [PASO 2/5] Adaptando contenido para cada red social...")
    
    adaptaciones = {}
    redes_validas = []
    
    for red in request.target_networks:
        if red not in llm_service.PROMPTS_POR_RED:
            print(f"   ⚠️  Red '{red}' no soportada, omitiendo...")
            continue
        
        print(f"   🔄 Adaptando para {red.upper()}...")
        adaptacion = llm_service.adaptar_contenido(
            titulo=request.text[:50],
            contenido=request.text,
            red_social=red
        )
        
        if "error" in adaptacion:
            print(f"   ❌ Error en {red}: {adaptacion['error']}")
            adaptaciones[red] = {"error": adaptacion["error"]}
        else:
            print(f"   ✅ {red.upper()} adaptado")
            adaptaciones[red] = adaptacion
            redes_validas.append(red)
    
    if not redes_validas:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "no_valid_networks",
                "mensaje": "No se pudo adaptar contenido para ninguna red válida",
                "redes_solicitadas": request.target_networks
            }
        )
    
    print(f"\n✅ Adaptaciones completadas: {len(redes_validas)} redes\n")
    
    # ═══════════════════════════════════════════════════════════════
    # 🎨 PASO 3: GENERAR RECURSOS (imágenes, videos)
    # ═══════════════════════════════════════════════════════════════
    print("🎨 [PASO 3/5] Generando recursos multimedia...")
    
    recursos = {
        "imagen_instagram": None,
        "imagen_whatsapp": None,
        "video_tiktok": None
    }
    
    # Imagen para Instagram (si está en la lista)
    if "instagram" in redes_validas and "instagram" in adaptaciones:
        print("   🎨 Generando imagen para Instagram...")
        prompt_img = adaptaciones["instagram"].get(
            "suggested_image_prompt", 
            f"Universidad UAGRM: {request.text[:100]}"
        )
        recursos["imagen_instagram"] = llm_service.generar_imagen_ia(prompt_img)
        print(f"   ✅ Imagen Instagram generada")
    
    # Imagen para WhatsApp Status (si está en la lista)
    if "whatsapp" in redes_validas:
        print("   🎨 Generando imagen para WhatsApp Status...")
        prompt_img = f"Universidad UAGRM: {request.text[:100]}"
        recursos["imagen_whatsapp"] = llm_service.generar_imagen_ia_base64(prompt_img)
        print(f"   ✅ Imagen WhatsApp generada")
    
    # Video para TikTok (si está en la lista)
    if "tiktok" in redes_validas and "tiktok" in adaptaciones:
        print("   🎬 Generando video para TikTok...")
        texto_adaptado = adaptaciones["tiktok"].get("text", request.text)
        recursos["video_tiktok"] = llm_service.generar_video_tiktok(
            texto_adaptado, 
            adaptaciones["tiktok"]
        )
        if recursos["video_tiktok"]:
            print(f"   ✅ Video TikTok generado")
        else:
            print(f"   ❌ Error generando video TikTok")
            redes_validas.remove("tiktok")
    
    print(f"\n✅ Recursos multimedia generados\n")
    
    # ═══════════════════════════════════════════════════════════════
    # 📤 PASO 4: PUBLICAR EN CADA RED SOCIAL
    # ═══════════════════════════════════════════════════════════════
    print("📤 [PASO 4/5] Publicando en redes sociales...")
    
    resultados = {}
    exitosos = 0
    fallidos = 0
    
    for red in redes_validas:
        print(f"\n   📤 Publicando en {red.upper()}...")
        
        try:
            adaptacion = adaptaciones[red]
            texto_adaptado = adaptacion.get("text", request.text)
            
            # Agregar hashtags si existen
            if "hashtags" in adaptacion and adaptacion["hashtags"]:
                hashtags_str = " ".join(adaptacion["hashtags"])
                if not any(tag in texto_adaptado for tag in adaptacion["hashtags"]):
                    texto_adaptado = f"{texto_adaptado}\n\n{hashtags_str}"
            
            # ─────────────────────────────────────────────────────
            # 🔵 FACEBOOK (solo texto)
            # ─────────────────────────────────────────────────────
            if red == "facebook":
                result = social_services.post_to_facebook(
                    text=texto_adaptado,
                    image_url=None
                )
                
                if "error" in result:
                    resultados["facebook"] = {
                        "estado": "error",
                        "error": result["error"],
                        "adaptacion": adaptacion
                    }
                    fallidos += 1
                    print(f"   ❌ Facebook falló: {result['error']}")
                else:
                    post_id = result.get("id") or result.get("post_id")
                    link = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else None
                    
                    resultados["facebook"] = {
                        "estado": "exitoso",
                        "id": post_id,
                        "link": link,
                        "adaptacion": adaptacion
                    }
                    exitosos += 1
                    print(f"   ✅ Facebook publicado: {link}")
            
            # ─────────────────────────────────────────────────────
            # 📸 INSTAGRAM (texto + imagen)
            # ─────────────────────────────────────────────────────
            elif red == "instagram":
                if not recursos["imagen_instagram"]:
                    resultados["instagram"] = {
                        "estado": "error",
                        "error": "No se pudo generar imagen",
                        "adaptacion": adaptacion
                    }
                    fallidos += 1
                    print(f"   ❌ Instagram falló: sin imagen")
                    continue
                
                result = social_services.post_to_instagram(
                    text=texto_adaptado,
                    image_url=recursos["imagen_instagram"]
                )
                
                if "error" in result:
                    resultados["instagram"] = {
                        "estado": "error",
                        "error": result["error"],
                        "adaptacion": adaptacion
                    }
                    fallidos += 1
                    print(f"   ❌ Instagram falló: {result['error']}")
                else:
                    resultados["instagram"] = {
                        "estado": "exitoso",
                        "id": result.get("id"),
                        "link": result.get("permalink"),
                        "imagen_url": recursos["imagen_instagram"],
                        "adaptacion": adaptacion
                    }
                    exitosos += 1
                    print(f"   ✅ Instagram publicado: {result.get('permalink')}")
            
            # ─────────────────────────────────────────────────────
            # 💼 LINKEDIN (texto profesional)
            # ─────────────────────────────────────────────────────
            elif red == "linkedin":
                result = social_services.post_to_linkedin(text=texto_adaptado)
                
                if "error" in result:
                    resultados["linkedin"] = {
                        "estado": "error",
                        "error": result["error"],
                        "adaptacion": adaptacion
                    }
                    fallidos += 1
                    print(f"   ❌ LinkedIn falló: {result['error']}")
                else:
                    post_urn = result.get("id", "")
                    link = f"https://www.linkedin.com/feed/update/{post_urn}" if post_urn else None
                    
                    resultados["linkedin"] = {
                        "estado": "exitoso",
                        "id": post_urn.split(":")[-1] if ":" in post_urn else post_urn,
                        "link": link,
                        "adaptacion": adaptacion
                    }
                    exitosos += 1
                    print(f"   ✅ LinkedIn publicado: {link}")
            
            # ─────────────────────────────────────────────────────
            # 💚 WHATSAPP STATUS (imagen + texto)
            # ─────────────────────────────────────────────────────
            elif red == "whatsapp":
                if not recursos["imagen_whatsapp"]:
                    resultados["whatsapp"] = {
                        "estado": "error",
                        "error": "No se pudo generar imagen",
                        "adaptacion": adaptacion
                    }
                    fallidos += 1
                    print(f"   ❌ WhatsApp falló: sin imagen")
                    continue
                
                result = social_services.post_whatsapp_status(
                    text=texto_adaptado,
                    image_url=recursos["imagen_whatsapp"]
                )
                
                if "error" in result:
                    resultados["whatsapp"] = {
                        "estado": "error",
                        "error": result["error"],
                        "adaptacion": adaptacion
                    }
                    fallidos += 1
                    print(f"   ❌ WhatsApp falló: {result['error']}")
                else:
                    resultados["whatsapp"] = {
                        "estado": "exitoso",
                        "id": result.get("id"),
                        "status": result.get("status"),
                        "adaptacion": adaptacion
                    }
                    exitosos += 1
                    print(f"   ✅ WhatsApp Status publicado")
            
            # ─────────────────────────────────────────────────────
            # 🎵 TIKTOK (video generado)
            # ─────────────────────────────────────────────────────
            elif red == "tiktok":
                if not recursos["video_tiktok"]:
                    resultados["tiktok"] = {
                        "estado": "error",
                        "error": "No se pudo generar video",
                        "adaptacion": adaptacion
                    }
                    fallidos += 1
                    print(f"   ❌ TikTok falló: sin video")
                    continue
                
                result = social_services.post_to_tiktok(
                    text=texto_adaptado,
                    video_path=recursos["video_tiktok"],
                    privacy="SELF_ONLY"
                )
                
                # Limpiar video temporal
                if recursos["video_tiktok"] and os.path.exists(recursos["video_tiktok"]):
                    os.unlink(recursos["video_tiktok"])
                
                if "error" in result:
                    resultados["tiktok"] = {
                        "estado": "error",
                        "error": result["error"],
                        "mensaje": result.get("mensaje", "Error al publicar en TikTok"),
                        "adaptacion": adaptacion
                    }
                    fallidos += 1
                    print(f"   ❌ TikTok falló: {result['error']}")
                else:
                    # 🔗 RETORNAR TODA LA INFO INCLUYENDO share_url
                    resultados["tiktok"] = {
                        "estado": "exitoso",
                        "publish_id": result.get("publish_id"),
                        "video_id": result.get("video_id"),
                        "share_url": result.get("share_url"),  # 🔗 ENLACE DEL VIDEO
                        "privacy": result.get("privacy"),
                        "mode": result.get("mode"),
                        "size_mb": result.get("size_mb"),
                        "mensaje": result.get("mensaje"),
                        "como_ver": result.get("como_ver"),  # 📱 INSTRUCCIONES
                        "cuenta": result.get("cuenta", "@limberg818"),
                        "visibilidad": result.get("visibilidad"),
                        "nota": result.get("nota"),
                        "adaptacion": adaptacion
                    }
                    exitosos += 1
                    
                    # Log del share_url
                    share_url = result.get("share_url")
                    if share_url:
                        print(f"   ✅ TikTok publicado: {share_url}")
                    else:
                        print(f"   ✅ TikTok publicado (sin share_url público)")
        
        except Exception as e:
            resultados[red] = {
                "estado": "error",
                "error": f"Excepción: {str(e)}",
                "adaptacion": adaptacion
            }
            fallidos += 1
            print(f"   ❌ {red.upper()} falló con excepción: {e}")
    
    # ═══════════════════════════════════════════════════════════════
    # 📊 PASO 5: RESUMEN FINAL
    # ═══════════════════════════════════════════════════════════════
    tiempo_total = time.time() - inicio
    
    print("\n" + "="*70)
    print("📊 [PASO 5/5] RESUMEN DE PUBLICACIONES")
    print("="*70)
    print(f"✅ Exitosos: {exitosos}")
    print(f"❌ Fallidos: {fallidos}")
    print(f"⏱️  Tiempo total: {tiempo_total:.1f} segundos")
    print("="*70 + "\n")
    
    resumen = {
        "total_redes": len(request.target_networks),
        "redes_validas": len(redes_validas),
        "exitosos": exitosos,
        "fallidos": fallidos,
        "tasa_exito": f"{(exitosos/len(redes_validas)*100):.1f}%" if redes_validas else "0%",
        "tiempo_segundos": round(tiempo_total, 1)
    }
    
    return {
        "validacion": validacion,
        "resultados": resultados,
        "resumen": resumen
    }