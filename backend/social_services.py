import httpx
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")  # ← NUEVO: Agrega esto a tu .env

META_GRAPH_URL = "https://graph.facebook.com/v19.0"


def post_to_facebook(text: str, image_url: str):
    """
    Publica una FOTO con texto en una Página de Facebook.
    """
    post_url = f"{META_GRAPH_URL}/{PAGE_ID}/photos"
    payload = {
        'caption': text,
        'url': image_url,
        'access_token': META_TOKEN
    }
    
    try:
        logging.info(f"Publicando en Facebook: {text[:20]}...")
        response = httpx.post(post_url, data=payload)
        response.raise_for_status() 
        
        result = response.json()
        logging.info(f"✅ Publicado en Facebook. Post ID: {result['id']}")
        return result
        
    except httpx.HTTPStatusError as e:
        logging.error(f"❌ Error al publicar en Facebook: {e.response.json()}")
        return {"error": f"Error de API: {e.response.json()}"}
    except Exception as e:
        logging.error(f"❌ Error inesperado en Facebook: {e}")
        return {"error": f"Error inesperado: {str(e)}"}


def post_to_instagram(text: str, image_url: str):
    """
    Publica una FOTO con texto en Instagram.
    Flujo de 2 pasos: crear contenedor → publicar
    """
    
    # VALIDACIÓN IMPORTANTE
    if not IG_ACCOUNT_ID:
        logging.error("❌ INSTAGRAM_ACCOUNT_ID no configurado en .env")
        return {
            "error": "Instagram Account ID no configurado. "
                     "Ejecuta verify_instagram.py para obtenerlo"
        }
    
    logging.info(f"Publicando en Instagram: {text[:20]}...")
    
    try:
        # --- PASO 1: Crear el "Contenedor" de la imagen ---
        logging.info("Instagram - Paso 1: Creando contenedor...")
        
        # ← CAMBIO CRÍTICO: Usar IG_ACCOUNT_ID en lugar de PAGE_ID
        container_url = f"{META_GRAPH_URL}/{IG_ACCOUNT_ID}/media"
        
        container_payload = {
            'image_url': image_url,
            'caption': text,
            'access_token': META_TOKEN
        }
        
        response_container = httpx.post(container_url, data=container_payload)
        response_container.raise_for_status()
        container_id = response_container.json()['id']
        logging.info(f"✅ Contenedor creado: {container_id}")

        # --- PASO 2: Publicar el Contenedor ---
        logging.info("Instagram - Paso 2: Publicando contenedor...")
        
        # ← CAMBIO CRÍTICO: Usar IG_ACCOUNT_ID en lugar de PAGE_ID
        publish_url = f"{META_GRAPH_URL}/{IG_ACCOUNT_ID}/media_publish"
        
        publish_payload = {
            'creation_id': container_id,
            'access_token': META_TOKEN
        }
        
        response_publish = httpx.post(publish_url, data=publish_payload)
        response_publish.raise_for_status()
        result = response_publish.json()
        
        logging.info(f"✅ Publicado en Instagram. Media ID: {result['id']}")
        return result

    except httpx.HTTPStatusError as e:
        error_data = e.response.json()
        logging.error(f"❌ Error al publicar en Instagram: {error_data}")
        
        # Mensajes de ayuda según el error
        if error_data.get('error', {}).get('error_subcode') == 33:
            logging.error("💡 Este error indica que:")
            logging.error("   1. La página no tiene Instagram conectado")
            logging.error("   2. O el token no tiene permisos de Instagram")
            logging.error("   Ejecuta verify_instagram.py para diagnosticar")
        
        return {"error": f"Error de API: {error_data}"}
        
    except Exception as e:
        logging.error(f"❌ Error inesperado en Instagram: {e}")
        return {"error": f"Error inesperado: {str(e)}"}

def get_linkedin_user_urn():
    """
    Helper: Para publicar en LinkedIn, primero necesitas tu "URN" (ID de persona).
    """
    LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    profile_url = "https://api.linkedin.com/v2/me"
    headers = {'Authorization': f'Bearer {LINKEDIN_TOKEN}'}
    
    try:
        response = httpx.get(profile_url, headers=headers)
        response.raise_for_status()
        return response.json()['id']
    except httpx.HTTPStatusError as e:
        logging.error(f"Error al obtener URN de LinkedIn: {e.response.json()}")
        return None


def post_to_linkedin(text: str):
    """
    Publica un POST de solo TEXTO en LinkedIn.
    """
    LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    logging.info(f"Publicando en LinkedIn: {text[:20]}...")
    
    author_urn = get_linkedin_user_urn()
    if not author_urn:
        return {"error": "No se pudo obtener el URN de LinkedIn. Revisa tu token."}
    
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        'Authorization': f'Bearer {LINKEDIN_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    try:
        response = httpx.post(post_url, json=payload, headers=headers)
        response.raise_for_status()
        
        logging.info("✅ Publicado en LinkedIn con éxito.")
        return response.json()
        
    except httpx.HTTPStatusError as e:
        logging.error(f"❌ Error al publicar en LinkedIn: {e.response.json()}")
        return {"error": f"Error de API: {e.response.json()}"}
    except Exception as e:
        logging.error(f"❌ Error inesperado en LinkedIn: {e}")
        return {"error": f"Error inesperado: {str(e)}"}