from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import social_services
import schemas
import llm_service

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API del Sistema Multi-Red Social funcionando"}


@app.post("/api/posts/adapt")
def adapt_post_content(request: schemas.AdaptRequest):
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
def test_post_facebook(request: schemas.TestPostRequest):
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
def test_post_instagram(request: schemas.TestPostRequest):
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
def test_post_linkedin(request: schemas.TestPostRequestLinkedIn):
    """ 
    Endpoint para publicar en LinkedIn 
    (SIN adaptación por ahora)
    """
    result = social_services.post_to_linkedin(text=request.text)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result