import httpx
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

META_TOKEN = os.getenv("META_ACCESS_TOKEN")
PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
IG_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

META_GRAPH_URL = "https://graph.facebook.com/v19.0"


def post_to_facebook(text: str, image_url: str = None):
    """
    Publica en Facebook.
    - Si image_url está presente: publica foto con texto
    - Si image_url es None: publica solo texto
    """
    
    if image_url:
        post_url = f"{META_GRAPH_URL}/{PAGE_ID}/photos"
        payload = {
            'caption': text,
            'url': image_url,
            'access_token': META_TOKEN
        }
    else:
        post_url = f"{META_GRAPH_URL}/{PAGE_ID}/feed"
        payload = {
            'message': text,
            'access_token': META_TOKEN
        }
    
    try:
        logging.info(f"Publicando en Facebook: {text[:20]}...")
        response = httpx.post(post_url, data=payload)
        response.raise_for_status() 
        
        result = response.json()
        logging.info(f"✅ Publicado en Facebook. Post ID: {result.get('id', result.get('post_id', 'N/A'))}")
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
    Luego obtiene el permalink real.
    """
    
    # VALIDACIÓN IMPORTANTE
    if not IG_ACCOUNT_ID:
        logging.error("❌ INSTAGRAM_ACCOUNT_ID no configurado en .env")
        return {
            "error": "Instagram Account ID no configurado. "
                     "Ejecuta verify_instagram.py para obtenerlo"
        }
    
    if not image_url:
        logging.error("❌ Instagram requiere una imagen")
        return {"error": "Instagram requiere una URL de imagen"}
    
    logging.info(f"Publicando en Instagram: {text[:20]}...")
    
    try:
        # --- PASO 1: Crear el "Contenedor" de la imagen ---
        logging.info("Instagram - Paso 1: Creando contenedor...")
        
        container_url = f"{META_GRAPH_URL}/{IG_ACCOUNT_ID}/media"
        
        container_payload = {
            'image_url': image_url,
            'caption': text,
            'access_token': META_TOKEN
        }
        
        response_container = httpx.post(container_url, data=container_payload, timeout=60.0)
        response_container.raise_for_status()
        container_id = response_container.json()['id']
        logging.info(f"✅ Contenedor creado: {container_id}")

        # --- PASO 2: Publicar el Contenedor ---
        logging.info("Instagram - Paso 2: Publicando contenedor...")
        
        publish_url = f"{META_GRAPH_URL}/{IG_ACCOUNT_ID}/media_publish"
        
        publish_payload = {
            'creation_id': container_id,
            'access_token': META_TOKEN
        }
        
        response_publish = httpx.post(publish_url, data=publish_payload, timeout=60.0)
        response_publish.raise_for_status()
        result = response_publish.json()
        media_id = result['id']
        
        logging.info(f"✅ Publicado en Instagram. Media ID: {media_id}")
        
        # --- PASO 3: Obtener el permalink ---
        logging.info("Instagram - Paso 3: Obteniendo permalink...")
        
        permalink_url = f"{META_GRAPH_URL}/{media_id}"
        permalink_params = {
            'fields': 'id,permalink',
            'access_token': META_TOKEN
        }
        
        response_permalink = httpx.get(permalink_url, params=permalink_params, timeout=10.0)
        response_permalink.raise_for_status()
        permalink_data = response_permalink.json()
        
        permalink = permalink_data.get('permalink', None)
        logging.info(f"✅ Permalink obtenido: {permalink}")
        
        # Agregar permalink al resultado
        result['permalink'] = permalink
        
        return result

    except httpx.HTTPStatusError as e:
        error_data = e.response.json()
        logging.error(f"❌ Error al publicar en Instagram: {error_data}")
        
        if error_data.get('error', {}).get('error_subcode') == 33:
            logging.error("💡 Este error indica que:")
            logging.error("   1. La página no tiene Instagram conectado")
            logging.error("   2. O el token no tiene permisos de Instagram")
            logging.error("   Ejecuta verify_instagram.py para diagnosticar")
        
        return {"error": f"Error de API: {error_data}"}
        
    except Exception as e:
        logging.error(f"❌ Error inesperado en Instagram: {e}")
        return {"error": f"Error inesperado: {str(e)}"}


def get_linkedin_user_info():
    """
    🆕 MÉTODO CORREGIDO: Usa el nuevo endpoint /v2/userinfo
    Requiere que tu token tenga los scopes: openid, profile
    
    Retorna el 'sub' (identificador único del usuario)
    """
    LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    # 🔥 NUEVO ENDPOINT: /v2/userinfo en lugar de /v2/me
    userinfo_url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        'Authorization': f'Bearer {LINKEDIN_TOKEN}'
    }
    
    try:
        logging.info("LinkedIn - Obteniendo información de usuario con /v2/userinfo...")
        response = httpx.get(userinfo_url, headers=headers, timeout=10.0)
        response.raise_for_status()
        
        user_data = response.json()
        # El nuevo endpoint retorna 'sub' en lugar de 'id'
        user_sub = user_data.get('sub')
        
        logging.info(f"✅ Usuario LinkedIn obtenido: {user_data.get('name')} (sub: {user_sub})")
        return user_sub
        
    except httpx.HTTPError as e:
        # Cambio: HTTPStatusError -> HTTPError (compatible con versiones antiguas)
        try:
            error_data = e.response.json()
            logging.error(f"❌ Error al obtener URN de LinkedIn: {error_data}")
        except:
            logging.error(f"❌ Error HTTP: {e}")
        
        logging.error("💡 Posibles causas:")
        logging.error("   1. Tu token no tiene el scope 'openid' o 'profile'")
        logging.error("   2. El token ha expirado (duran 60 días)")
        logging.error("   3. Necesitas regenerar el token con los scopes correctos")
        logging.error("   4. Verifica que la URL sea correcta: /v2/userinfo")
        return None
    except Exception as e:
        logging.error(f"❌ Error inesperado: {e}")
        return None


def post_to_linkedin(text: str):
    """
    🆕 MÉTODO MEJORADO: Publica un POST de solo TEXTO en LinkedIn.
    Ahora usa el nuevo método get_linkedin_user_info()
    """
    LINKEDIN_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    logging.info(f"Publicando en LinkedIn: {text[:20]}...")
    
    # Obtener el identificador del usuario
    user_sub = get_linkedin_user_info()
    if not user_sub:
        return {
            "error": "No se pudo obtener el identificador de LinkedIn. "
                     "Verifica que tu token tenga los scopes 'openid' y 'profile'."
        }
    
    post_url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        'Authorization': f'Bearer {LINKEDIN_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    # 🔥 USAMOS 'sub' en lugar de un URN completo
    payload = {
        "author": f"urn:li:person:{user_sub}",
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
        response = httpx.post(post_url, json=payload, headers=headers, timeout=30.0)
        response.raise_for_status()
        
        logging.info("✅ Publicado en LinkedIn con éxito.")
        return response.json()
        
    except httpx.HTTPStatusError as e:
        error_data = e.response.json()
        logging.error(f"❌ Error al publicar en LinkedIn: {error_data}")
        return {"error": f"Error de API: {error_data}"}
    except Exception as e:
        logging.error(f"❌ Error inesperado en LinkedIn: {e}")
        return {"error": f"Error inesperado: {str(e)}"}