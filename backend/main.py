from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Para permitir que React se conecte

# Importa tus modelos Pydantic y tu servicio de LLM
import schemas
import llm_service

app = FastAPI()

# Configuración de CORS (¡Importante para conectar React!)
# Permite que tu app de React (que corre en localhost:5173 o similar)
# haga llamadas a tu backend (que corre en localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes restringirlo a "http://localhost:5173"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API del Sistema Multi-Red Social funcionando"}


# ---- ESTE ES EL ENDPOINT DE LA CLASE 2 ----
@app.post("/api/posts/adapt")
def adapt_post_content(request: schemas.AdaptRequest):
    """
    Recibe un título, contenido y lista de redes,
    y devuelve las adaptaciones generadas por el LLM.
    """
    
    print(f"Recibida solicitud para adaptar: {request.titulo}")
    
    # 1. Prepara el diccionario de respuesta
    adaptaciones_finales = {}
    
    # 2. Hace un bucle sobre las redes solicitadas
    for red in request.target_networks:
        if red not in llm_service.PROMPTS_POR_RED:
            adaptaciones_finales[red] = {"error": f"Red '{red}' no soportada."}
            continue

        # 3. Llama al servicio de adaptación para cada red
        # (Esto es sincrónico, uno por uno. En Clase 4 lo haremos asíncrono)
        resultado = llm_service.adaptar_contenido(
            titulo=request.titulo,
            contenido=request.contenido,
            red_social=red
        )
        
        adaptaciones_finales[red] = resultado

    # 4. Construye y devuelve la respuesta completa
    if not adaptaciones_finales:
        raise HTTPException(status_code=400, detail="No se especificaron redes válidas.")

    # Usamos el schema de Pydantic para la respuesta
    return schemas.AdaptResponse(data=adaptaciones_finales)



    # ---------------------------------------------------------------------------------

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

# --- Fin del archivo llm_service.py ---