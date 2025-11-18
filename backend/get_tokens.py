import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Obtén estos valores de tu app de Meta
APP_ID = "919997474522944"  # Lo encuentras en Settings > Basic
APP_SECRET = "4c7e951dded9f90280b52570d27a326e"  # Lo encuentras en Settings > Basic
SHORT_LIVED_TOKEN = "EAANEu5qpx0ABP9C9vFsOk16qmkxXOqt55aZBhfoFPZBqrrkQdctpnw4q306TjeEwvlbFzrngUPUeZC7oAe8M6SCpQvObxVJIe7ovyoLW2fVYD2JF0gxpbYaragswoOGdjq5Xk3x6yiqn4qDtT7yU2RO6MQykqVCKebuCYpSQjrH9qJuRTJQNE1NxVJ4rnTmLmp5yt5LiIHtAwhN52IAlVrufTjRNzePZA6jO5Go2e5YZD"  # El token que acabas de generar

def get_long_lived_token():
    """
    Convierte un token de corta duración a uno de larga duración (60 días)
    """
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": APP_ID,
        "client_secret": APP_SECRET,
        "fb_exchange_token": SHORT_LIVED_TOKEN
    }
    
    response = httpx.get(url, params=params)
    result = response.json()
    
    if "access_token" in result:
        print("✅ Long-Lived Token obtenido:")
        print(result["access_token"])
        print(f"\nExpira en: {result.get('expires_in', 'N/A')} segundos")
        return result["access_token"]
    else:
        print("❌ Error al obtener token:")
        print(result)
        return None

def get_page_token(long_lived_token, page_id):
    """
    Obtiene el Page Access Token usando el Long-Lived User Token
    """
    url = f"https://graph.facebook.com/v19.0/{page_id}"
    params = {
        "fields": "access_token",
        "access_token": long_lived_token
    }
    
    response = httpx.get(url, params=params)
    result = response.json()
    
    if "access_token" in result:
        print("\n✅ Page Access Token obtenido:")
        print(result["access_token"])
        print("\n🔄 Actualiza tu .env con este token en META_ACCESS_TOKEN")
        return result["access_token"]
    else:
        print("❌ Error al obtener Page Token:")
        print(result)
        return None

if __name__ == "__main__":
    print("🔐 Paso 1: Obteniendo Long-Lived User Token...")
    long_lived = get_long_lived_token()
    
    if long_lived:
        print("\n🔐 Paso 2: Obteniendo Page Access Token...")
        page_token = get_page_token(long_lived, "825436773993490")
        
        if page_token:
            print("\n✨ ¡Proceso completado!")
            print("📝 Copia el Page Access Token de arriba y actualiza tu .env")