import httpx
import webbrowser
import secrets
import hashlib
import base64
import time
import os
from urllib.parse import urlencode

CLIENT_KEY = "sbawibid7hcoe5se40"
CLIENT_SECRET = input("📝 Ingresa tu CLIENT_SECRET: ").strip()

# Pedir la URL de ngrok
print("\n" + "="*60)
print("🌐 CONFIGURACIÓN DE NGROK")
print("="*60)
print("\nEn la ventana de ngrok, busca la línea 'Forwarding'")
print("Ejemplo: https://abc123.ngrok-free.app -> http://localhost:3000\n")
NGROK_URL = input("📋 Pega aquí tu URL de ngrok (sin /callback): ").strip()
REDIRECT_URI = f"{NGROK_URL}/callback"

print(f"\n✅ Redirect URI: {REDIRECT_URI}")
print("\n⚠️  IMPORTANTE: Registra esta URL en TikTok Developers:")
print(f"   {REDIRECT_URI}\n")
input("👉 Presiona ENTER cuando hayas registrado la URL...")

# PKCE
def generate_code_verifier():
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)

# Autorización
auth_params = {
    "client_key": CLIENT_KEY,
    "scope": "user.info.basic,video.upload,video.publish",
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "state": "test123",
    "code_challenge": code_challenge,
    "code_challenge_method": "S256"
}

auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(auth_params)}"

print("\n" + "="*60)
print("🔓 AUTORIZANDO EN TIKTOK")
print("="*60)
print("\n1. Se abrirá tu navegador")
print("2. Inicia sesión en TikTok")
print("3. Autoriza la aplicación")
print("4. El servidor capturará el code automáticamente\n")

input("👉 Presiona ENTER para abrir el navegador...")
webbrowser.open(auth_url)

print("\n⏳ Esperando autorización (máximo 2 minutos)...")

# Esperar el code
max_wait = 120
for i in range(max_wait):
    if os.path.exists('tiktok_code.txt'):
        break
    time.sleep(1)
    if i % 10 == 0:
        print(f"   Esperando... ({i}s)")

if not os.path.exists('tiktok_code.txt'):
    print("❌ Timeout: No se recibió el code")
    exit(1)

with open('tiktok_code.txt', 'r') as f:
    code = f.read().strip()

print(f"\n✅ Code obtenido: {code[:20]}...\n")

# Obtener token
print("="*60)
print("🔄 OBTENIENDO ACCESS TOKEN")
print("="*60)

token_data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": code,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
    "code_verifier": code_verifier
}

try:
    response = httpx.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        data=token_data,
        timeout=30.0
    )
    response.raise_for_status()
    token_response = response.json()
    
    if "access_token" in token_response:
        print("\n🎉 ¡ACCESS TOKEN OBTENIDO!\n")
        print("="*60)
        print("📝 AGREGA ESTO A TU .env")
        print("="*60)
        print(f"\nTIKTOK_CLIENT_KEY={CLIENT_KEY}")
        print(f"TIKTOK_CLIENT_SECRET={CLIENT_SECRET}")
        print(f"TIKTOK_ACCESS_TOKEN={token_response['access_token']}")
        print(f"TIKTOK_REFRESH_TOKEN={token_response.get('refresh_token', 'N/A')}")
        print(f"\n⏰ Expira en: {token_response['expires_in']//3600} horas")
    else:
        print("❌ Error:")
        print(token_response)
        
except Exception as e:
    print(f"❌ Error: {e}")

# Limpiar
if os.path.exists('tiktok_code.txt'):
    os.remove('tiktok_code.txt')

print("\n✅ Proceso completado")