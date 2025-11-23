import httpx
import os
from dotenv import load_dotenv

load_dotenv()

TIKTOK_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

print("="*60)
print("🔍 DEBUG: SUBIDA DE VIDEO A TIKTOK")
print("="*60)

# Crear un video de prueba pequeño (1 KB)
test_video_path = "test_video.mp4"
test_data = b"0" * 1024  # 1 KB de datos

with open(test_video_path, 'wb') as f:
    f.write(test_data)

video_size = os.path.getsize(test_video_path)
print(f"✅ Video de prueba creado: {video_size} bytes\n")

# PASO 1: Inicializar
print("Paso 1: Inicializando subida...")

headers = {
    "Authorization": f"Bearer {TIKTOK_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "source_info": {
        "source": "FILE_UPLOAD",
        "video_size": video_size,
        "chunk_size": video_size,
        "total_chunk_count": 1
    }
}

response = httpx.post(
    "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/",
    json=payload,
    headers=headers,
    timeout=10.0
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    publish_id = data["data"]["publish_id"]
    upload_url = data["data"]["upload_url"]
    
    print(f"✅ Publish ID: {publish_id}")
    print(f"✅ Upload URL: {upload_url}\n")
    
    # PASO 2: Subir
    print("Paso 2: Subiendo video...")
    
    with open(test_video_path, 'rb') as f:
        video_bytes = f.read()
    
    # Probar 3 métodos diferentes
    methods = [
        {
            "name": "Método 1: Solo Content-Type",
            "headers": {
                "Content-Type": "video/mp4"
            }
        },
        {
            "name": "Método 2: Con Content-Length",
            "headers": {
                "Content-Type": "video/mp4",
                "Content-Length": str(len(video_bytes))
            }
        },
        {
            "name": "Método 3: Con Content-Range",
            "headers": {
                "Content-Type": "video/mp4",
                "Content-Length": str(len(video_bytes)),
                "Content-Range": f"bytes 0-{len(video_bytes)-1}/{len(video_bytes)}"
            }
        }
    ]
    
    for method in methods:
        print(f"\n{method['name']}...")
        
        try:
            response_upload = httpx.put(
                upload_url,
                content=video_bytes,
                headers=method['headers'],
                timeout=30.0
            )
            
            print(f"  Status: {response_upload.status_code}")
            
            if response_upload.status_code in [200, 201, 204]:
                print(f"  ✅ ¡FUNCIONA!")
                print(f"  Response: {response_upload.text}")
                break
            else:
                print(f"  ❌ Falló")
                print(f"  Response: {response_upload.text[:200]}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
else:
    print(f"❌ Error en inicialización: {response.text}")

# Limpiar
if os.path.exists(test_video_path):
    os.remove(test_video_path)
    print(f"\n🗑️ Archivo de prueba eliminado")

print("\n" + "="*60)