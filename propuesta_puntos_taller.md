# Propuesta de Proyecto de Grado
**Módulo:** Taller de Grado I
**Desarrolladores:** [Tu Nombre] y [Nombre de tu compañero]

---

### Las posibles funciones.
El proyecto consiste en el desarrollo de la **"Plataforma Web Basada en Inteligencia Artificial para la Gestión y Automatización Omnicanal de Redes Sociales"**. Las funciones principales abarcan:
*   **Gestor Multi-marca Inteligente:** Administración de diferentes perfiles comerciales, permitiendo a la IA adaptar automáticamente el tono publicitario (formal, dinámico, etc.) según la marca seleccionada.
*   **Generador Transversal con IA (Multiformato):** A partir de un texto base muy corto (ej. *"Campaña de vacunación, 13:00 pm"*), el sistema despliega el contenido mágicamente para cada red: para Facebook genera el texto adaptado más una imagen; para Instagram adapta el texto y la imagen a su formato; para TikTok genera un video corto basado en el guion; para WhatsApp crea una imagen con texto para Estados; y para LinkedIn redacta solo texto formal. Todo con un solo botón.
*   **Dashboard de Vista Previa:** Renderizado en tiempo real que simula la interfaz nativa del teléfono móvil para revisar la apariencia exacta del post antes de publicarlo.
*   **Programación Diferida Asíncrona:** Calendario interactivo donde se asignan las publicaciones para que un sistema backend ("Worker") las publique de forma automática en la fecha y hora indicadas.
*   **Ingesta de Documentos (RAG):** El sistema lee resoluciones, normativas o folletos desde un archivo PDF y la IA abstrae los puntos clave para armar la campaña.
*   **Chatbot Reactivo Automático:** Integración con la red social para que el sistema escuche (24/7) los comentarios de las publicaciones y responda preguntas rutinarias del público de forma automática.

### La fundamentación teórica a aplicar en el software.
### La fundamentación teórica a aplicar en el software.
El desarrollo de este sistema no es empírico, sino que se fundamenta estrictamente en tres áreas académicas de las ciencias de la computación y de negocios:

*   **Inteligencia Artificial y Procesamiento de Lenguaje Natural (PLN):** Es la base teórica que explica cómo lograr que una computadora pueda leer, comprender y generar textos como un humano. Aplicaremos la teoría de los "Modelos de Lenguaje Grande" (LLM) para que el sistema redacte anuncios con sentido lógico, y métodos de lectura autónoma para que comprenda documentos PDF y saque resúmenes de forma estructurada.
*   **Ingeniería de Software en Sistemas Distribuidos:** Es la teoría sobre cómo construir arquitecturas web robustas donde los procesos ocurren "por detrás". En este proyecto aplicaremos los fundamentos de las "Arquitecturas Asíncronas y Colas de Tareas". Esto es lo que permite que el software pueda guardar una publicación hoy, agendarla, y despertarse solo a la semana siguiente para publicarla en Facebook, sin que se quiebre el sistema ni se pierdan los datos.
*   **Marketing Estratégico Computacional B2B:** Dado que es una plataforma dirigida a agencias, aplicaremos conceptos teóricos sobre negocios: cómo se debe distribuir contenido publicitario simultáneamente en varios canales ("Omnicanalidad") y cómo medir inteligentemente el impacto comercial de cada publicación en la audiencia.

### La problemática a resolver o caso de estudio.
**Contexto:** Las agencias de publicidad o los encargados de redes sociales de las empresas suelen manejar varias marcas al mismo tiempo (por ejemplo, le llevan el Facebook a una clínica, a una pizzería y a una universidad).
**El Problema:** Hoy en día, estas personas pierden muchísimo tiempo haciendo trabajo manual repetitivo. Si hay una promoción, tienen que escribir el anuncio de 5 formas distintas (formal para la clínica, alegre para la pizzería) y luego entrar a Facebook, TikTok e Instagram a copiar y pegar las imágenes una por una.
**La Solución:** Crear un sistema central (un único panel inteligente) que haga todo ese trabajo pesado solo. El usuario escribe una vez, y el sistema se encarga de crear los textos con el tono correcto para cada empresa, hacer las imágenes y dejarlas listas para publicar, ahorrando casi un 80% del tiempo que se perdía copiando y pegando cosas a mano.

### La novedad o el apoyo (Innovación).
La principal innovación que hace diferente a este proyecto en el mercado es que **el sistema funciona prácticamente solo**:
*   **Lee archivos enteros por su cuenta:** No necesitas perder tiempo escribiendo textos largos. Puedes simplemente subir el menú de tu restaurante en PDF, y el sistema solo lo lee, saca los platos, le pone emojis y crea los guiones publicitarios para toda la semana.
*   **Responde como un humano (24/7):** El software no solo publica la foto y ya. Se queda "despierto" esperando. Si a las 3 de la mañana un cliente comenta en la foto de Facebook "Precio por favor", el sistema lee el comentario, sabe de qué trata la foto y le contesta ahí mismo con amabilidad.

### Posibles tecnologías a usar en el desarrollo del proyecto.
El grado de complejidad del proyecto requiere un nivel avanzado de ingeniería de software distribuida para el trabajo coordinado de 2 desarrolladores:
*   **Frontend (Cliente Web UI/UX):** *React.js*, *Vite*, y *TailwindCSS* (para generar el *Dashboard* y los *Mockups* inyectables estilo nativo de *mobile*).
*   **Backend (Lógica de Negocios y APIs):** Plataforma web basada en *Python* con el *Framework* *FastAPI* (para permitir alta concurrencia asíncrona).
*   **Inteligencia Artificial (NLP/Multimedia):** Procesamiento a través de *OpenAI API* (GPT-4 / DALL-E) y la suite de orquestación analítica *LangChain*.
*   **Sistemas Asíncronos y Base de Datos:** Motores de Tareas como *Celery/Redis* para la calendarización, con apoyo en una base de datos de gestión relacional (*PostgreSQL/MySQL*).
*   **Módulos de Integración Externos (APIs de Referencia):** Conexión asegurada al nivel más alto mediante *OAuth 2.0* contra *Graph API (Meta Suite)*, *LinkedIn Platform* y *TikTok Developer API*.
