import httpx
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("TIKTOK_REFRESH_TOKEN")

print("🔄 Refrescando token de TikTok...")

url = "https://open.tiktokapis.com/v2/oauth/token/"

data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN
}

try:
    response = httpx.post(url, data=data, timeout=30.0)
    response.raise_for_status()
    
    result = response.json()
    
    print("\n✅ ¡TOKEN REFRESCADO!")
    print("="*60)
    print("📝 ACTUALIZA TU .env CON ESTOS VALORES:")
    print("="*60)
    print(f"\nTIKTOK_ACCESS_TOKEN={result['access_token']}")
    print(f"TIKTOK_REFRESH_TOKEN={result['refresh_token']}")
    print(f"\n⏰ Expira en: {result['expires_in']//3600} horas")
    
except Exception as e:
    print(f"❌ Error: {e}")