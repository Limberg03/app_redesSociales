### 2\. Contenido para `Desarrollo.md`

Y aquí está el contenido para tu archivo `Desarrollo.md`.

```markdown
# Documentación de Desarrollo - Módulo LLM (Clase 2)

## 1. Objetivo del Módulo

El objetivo de este módulo (Clase 2) fue implementar el prototipo del motor de adaptación de contenido. Esto incluye la configuración del cliente del LLM, la creación de un servicio de adaptación y la exposición de este servicio a través de un endpoint de API.

## 2. Stack Tecnológico Utilizado

* **Backend:** FastAPI
* **LLM API:** Google Gemini (SDK `google-generativeai`)
* **Definición de Datos:** Pydantic (integrado en FastAPI)
* **Variables de Entorno:** `python-dotenv`

## 3. Estructura de Archivos Relevante

backend/ ├── .env # Almacena la API Key de Gemini ├── main.py # Define el endpoint /api/posts/adapt ├── llm_service.py # Lógica principal de adaptación y prompts └── schemas.py # Define los modelos Pydantic (Request/Response)


## 4. Descripción de Componentes

### `backend/llm_service.py`

Este es el cerebro del módulo.

1.  **Configuración del Cliente (Gemini):**
    * Se carga la `GOOGLE_API_KEY` desde el archivo `.env` usando `load_dotenv()` y `os.environ`.
    * Se configura el cliente de `genai` con la clave.
    * Se inicializa el modelo (`gemini-1.5-pro-latest`) con una `GenerationConfig` crucial:
        ```python
        generation_config = genai.GenerationConfig(
            response_mime_type="application/json",
        )
        ```
    * Este ajuste fuerza a Gemini a devolver una respuesta en formato JSON, lo cual es vital para la estabilidad de la API.

2.  **`PROMPTS_POR_RED` (Diccionario):**
    * Un diccionario de Python almacena las plantillas de prompt (como strings) para cada red social (`facebook`, `instagram`, etc.).
    * Las plantillas usan placeholders de formato de Python (ej. `{titulo}`).

3.  **`adaptar_contenido(titulo, contenido, red_social)` (Función):**
    * Esta función recibe el título, el contenido y la red de destino.
    * Selecciona la plantilla de prompt correcta del diccionario.
    * Formatea el prompt usando `prompt_template.format(titulo=titulo, ...)`.
    * Llama a `model.generate_content(prompt_final)` para obtener la respuesta de la API.
    * La respuesta (`response.text`) es un *string* JSON, por lo que se utiliza `json.loads()` para convertirlo en un objeto de Python antes de devolverlo.

### `backend/schemas.py`

Este archivo define los "contratos" de datos.

* **`AdaptRequest(BaseModel)`:** Define el JSON que la API espera *recibir*.
    * `titulo: str`
    * `contenido: str`
    * `target_networks: List[str]`

* **`AdaptResponse(BaseOdel)`:** Define el JSON que la API *devuelve*. Se usa un diccionario genérico para permitir claves dinámicas (los nombres de las redes).
    * `data: Dict[str, Any]`

### `backend/main.py`

Este archivo expone la lógica como una API web.

* **`POST /api/posts/adapt` (Endpoint):**
    * Es el único endpoint implementado en esta fase.
    * Recibe un body JSON que se valida contra el schema `AdaptRequest`.
    * Crea un diccionario vacío `adaptaciones_finales`.
    * Itera sobre la lista `request.target_networks`.
    * Dentro del bucle, llama a `llm_service.adaptar_contenido()` para cada red.
    * Almacena el resultado de cada llamada en el diccionario `adaptaciones_finales`.
    * Finalmente, empaqueta este diccionario dentro de un objeto `AdaptResponse` y lo devuelve al cliente (Postman).

## 5. Lecciones Aprendidas y Manejo de Errores

1.  **`KeyError` en `.format()`:** El error más común durante el desarrollo. Ocurrió porque las llaves `{}` del JSON de ejemplo en los prompts entraban en conflicto con los placeholders `{titulo}`.
    * **Solución:** Se "escaparon" las llaves del JSON de ejemplo duplicándolas: `{` se convirtió en `{{` y `}` en `}}`.

2.  **`429 Resource exhausted` (Límite de Tasa):** Al probar las 5 redes a la vez, la API de Gemini devolvió este error.
    * **Causa:** La API gratuita tiene un límite de peticiones por minuto. El bucle `for` en `main.py` es sincrónico y ejecuta las 5 llamadas en menos de un segundo, superando el límite.
    * **Solución (Temporal):** Esperar unos segundos entre peticiones.
    * **Solución (Futura):** Este problema se abordará en la **Clase 4** con la implementación