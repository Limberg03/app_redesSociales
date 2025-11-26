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
    - 🆕 GENERACIÓN DE IMAGEN (igual que Instagram)
    """
    
    # 1. Validar contenido académico
    print("🔍 Validando contenido académico...")
    validacion = llm_service.validar_contenido_academico(request.text)
    
    if not validacion.get("es_academico", False):
        raise HTTPException(
            status_code=400, 
            detail={
                "error": "contenido_no_academico",
                "mensaje": "❌ Este contenido no es apropiado para publicación académica."
            }
        )
    
    print(f"✅ Contenido validado como académico: {validacion.get('razon')}")
    
    # 2. Adaptar contenido
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
    
    # 3. 🆕 GENERAR IMAGEN (igual que Instagram)
    print("🎨 Generando imagen para Facebook...")
    # prompt_imagen = f"Universidad UAGRM, tema académico: {request.text[:100]}"
    prompt_imagen = adaptacion.get("suggested_image_prompt", f"Universidad UAGRM, tema académico: {request.text[:100]}")
    imagen_url = llm_service.generar_imagen_ia(prompt_imagen)
    print(f"✅ Imagen generada: {imagen_url[:100]}...")
    
    # 4. Publicar en Facebook CON IMAGEN
    result = social_services.post_to_facebook(
        text=texto_adaptado,
        image_url=imagen_url  # ✅ CON IMAGEN
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # 5. Construir link del post
    post_id = result.get("id") or result.get("post_id")
    link_facebook = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}" if post_id else None
    
    # 6. 🆕 Retornar con imagen_generada
    return {
        "validacion": validacion,
        "adaptacion": adaptacion,
        "imagen_generada": {  # ✅ AGREGADO
            "url": imagen_url,
            "prompt": prompt_imagen
        },
        "publicacion": {
            "id": post_id,
            "link": link_facebook,
            "raw": result
        },
        "mensaje": "✅ Contenido académico validado, adaptado, imagen generada y publicado en Facebook"
    }