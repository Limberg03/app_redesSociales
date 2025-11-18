import httpx
import os
from dotenv import load_dotenv

load_dotenv()

PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
META_TOKEN = os.getenv("META_ACCESS_TOKEN")

def check_instagram_account():
    """
    Verifica si la página tiene una cuenta de Instagram conectada
    y obtiene el Instagram Business Account ID
    """
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}"
    params = {
        "fields": "instagram_business_account",
        "access_token": META_TOKEN
    }
    
    response = httpx.get(url, params=params)
    result = response.json()
    
    print("📱 Verificando cuenta de Instagram conectada...")
    print(f"Response: {result}\n")
    
    if "instagram_business_account" in result:
        ig_id = result["instagram_business_account"]["id"]
        print(f"✅ Instagram Business Account encontrada!")
        print(f"ID: {ig_id}")
        print(f"\n📝 Guarda este ID, lo necesitarás para publicar en Instagram")
        
        # Verificar permisos de la cuenta de Instagram
        check_instagram_permissions(ig_id)
        return ig_id
    else:
        print("❌ No se encontró cuenta de Instagram conectada")
        print("\n📌 Solución:")
        print("1. Ve a tu Página de Facebook")
        print("2. Configuración → Instagram")
        print("3. Conecta una cuenta de Instagram Business/Creator")
        return None

def check_instagram_permissions(ig_id):
    """
    Verifica los permisos de la cuenta de Instagram
    """
    url = f"https://graph.facebook.com/v19.0/{ig_id}"
    params = {
        "fields": "id,username,profile_picture_url",
        "access_token": META_TOKEN
    }
    
    response = httpx.get(url, params=params)
    result = response.json()
    
    print(f"\n📊 Información de la cuenta de Instagram:")
    if "username" in result:
        print(f"Username: @{result['username']}")
        print(f"✅ Token tiene permisos correctos para esta cuenta")
    else:
        print(f"❌ Error: {result}")
        print("El token no tiene permisos para esta cuenta de Instagram")

if __name__ == "__main__":
    check_instagram_account()