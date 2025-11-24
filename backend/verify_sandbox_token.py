import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TIKTOK_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

print("="*60)
print("🔍 VERIFICANDO TOKEN DE SANDBOX")
print("="*60)

if not TIKTOK_TOKEN:
    print("❌ TIKTOK_ACCESS_TOKEN no configurado en .env")
    exit(1)

print(f"✅ Token encontrado: {TIKTOK_TOKEN[:20]}...\n")

# Test: Verificar Direct Post con SELF_ONLY
print("Test: Probando Direct Post con SELF_ONLY (Sandbox)...")
try:
    response = httpx.post(
        "https://open.tiktokapis.com/v2/post/publish/video/init/",
        headers={
            "Authorization": f"Bearer {TIKTOK_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "post_info": {
                "title": "Test video",
                "privacy_level": "SELF_ONLY",  # Esto debe funcionar en Sandbox
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": 1000000,
                "chunk_size": 1000000,
                "total_chunk_count": 1
            }
        },
        timeout=10.0
    )
    
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ ¡PERFECTO! Puedes publicar con SELF_ONLY")
        print(f"Publish ID de prueba: {data['data']['publish_id']}")
        print("\n🎉 Tu configuración está correcta")
        print("💡 Ahora puedes publicar videos privados sin aprobación")
    else:
        error = response.json()
        error_code = error.get("error", {}).get("code", "")
        error_msg = error.get("error", {}).get("message", "")
        
        print(f"❌ Error: {error_code}")
        print(f"Mensaje: {error_msg}\n")
        
        if error_code == "unaudited_client_can_only_post_to_private_accounts":
            print("⚠️ SOLUCIÓN:")
            print("1. Ve a Developer Portal > Sandbox")
            print("2. Verifica que tu cuenta esté en 'Target Users'")
            print("3. Asegúrate de estar usando el token del Sandbox")
        elif error_code == "spam_risk_too_many_pending_share":
            print("⚠️ SOLUCIÓN:")
            print("1. Abre TikTok en tu móvil")
            print("2. Elimina videos pendientes/borradores")
            print("3. Espera 5-10 minutos e intenta de nuevo")
        else:
            print("💡 Detalles completos:")
            print(error)
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)