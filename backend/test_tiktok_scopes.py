import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TIKTOK_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

print("="*60)
print("🔍 VERIFICANDO PERMISOS DE TIKTOK")
print("="*60)

if not TIKTOK_TOKEN:
    print("❌ TIKTOK_ACCESS_TOKEN no configurado en .env")
    exit(1)

print(f"✅ Token encontrado: {TIKTOK_TOKEN[:20]}...\n")

# Test 1: Verificar info del usuario
print("Test 1: Obteniendo info del usuario...")
try:
    response = httpx.post(
        "https://open.tiktokapis.com/v2/post/publish/creator_info/query/",
        headers={
            "Authorization": f"Bearer {TIKTOK_TOKEN}",
            "Content-Type": "application/json"
        },
        timeout=10.0
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Usuario verificado")
        print(f"Data: {data}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)

# Test 2: Verificar si puede iniciar Direct Post
print("Test 2: Probando Direct Post (video.publish)...")
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
                "privacy_level": "SELF_ONLY"
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
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ video.publish (Direct Post) FUNCIONA")
        print(f"Response: {response.json()}")
    elif response.status_code == 403:
        error = response.json()
        error_code = error.get("error", {}).get("code", "")
        
        if error_code == "unaudited_client_can_only_post_to_private_accounts":
            print("⚠️ video.publish está habilitado pero tu app NO está aprobada")
            print("💡 SOLUCIÓN: Usa Draft Mode (video.upload) en su lugar")
        else:
            print(f"❌ Error 403: {error}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)

# Test 3: Verificar si puede iniciar Draft Upload
print("Test 3: Probando Draft Upload (video.upload)...")
try:
    response = httpx.post(
        "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
        headers={
            "Authorization": f"Bearer {TIKTOK_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": 1000000,
                "chunk_size": 1000000,
                "total_chunk_count": 1
            }
        },
        timeout=10.0
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ video.upload (Draft Mode) FUNCIONA")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("📊 RESUMEN")
print("="*60)
print("Si Test 2 falló con 'unaudited_client', usa Draft Mode (Test 3)")
print("Si Test 3 funcionó, modifica el código para usar video.upload")