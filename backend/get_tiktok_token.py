import httpx
import webbrowser
import secrets
import hashlib
import base64
from urllib.parse import urlencode, urlparse, parse_qs

# ============================================
# 🔧 CONFIGURACIÓN
# ============================================
CLIENT_KEY = "sbawibid7hcoe5se40"  # ✅ Ya lo tienes
CLIENT_SECRET = input("📝 Ingresa tu CLIENT_SECRET: ").strip()
REDIRECT_URI = "https://localhost/callback"
SCOPES = "user.info.basic,video.upload,video.publish"

# ============================================
# 🔐 GENERAR CODE VERIFIER Y CODE CHALLENGE
# ============================================
def generate_code_verifier():
    """Genera un code_verifier aleatorio (43-128 caracteres)"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')

def generate_code_challenge(verifier):
    """Genera el code_challenge desde el verifier usando SHA256"""
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')

code_verifier = generate_code_verifier()
code_challenge = generate_code_challenge(code_verifier)

print("\n🔐 Valores PKCE generados:")
print(f"Code Verifier: {code_verifier}")
print(f"Code Challenge: {code_challenge}\n")

# ============================================
# 📡 PASO 1: AUTORIZACIÓN
# ============================================
auth_params = {
    "client_key": CLIENT_KEY,
    "scope": SCOPES,
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "state": "test123",
    "code_challenge": code_challenge,
    "code_challenge_method": "S256"
}

auth_url = f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(auth_params)}"

print("=" * 60)
print("🔓 PASO 1: AUTORIZAR LA APLICACIÓN")
print("=" * 60)
print("\n1. Se abrirá tu navegador automáticamente")
print("2. Inicia sesión en TikTok si no lo has hecho")
print("3. Autoriza la aplicación")
print("4. Después te redirigirá a una página de error (ESTO ES NORMAL)")
print("5. Copia la URL COMPLETA de esa página de error\n")

input("👉 Presiona ENTER para abrir el navegador...")
webbrowser.open(auth_url)

print("\n⏳ Esperando autorización...")
print("(La página mostrará 'No se puede acceder al sitio' - ESTO ES NORMAL)\n")

# Usuario debe copiar la URL completa
callback_url = input("📋 Pega aquí la URL completa de la página de error:\n> ").strip()

# ============================================
# 🔍 EXTRAER EL CODE
# ============================================
try:
    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)
    code = params['code'][0]
    print(f"\n✅ Code obtenido correctamente: {code[:20]}...\n")
except Exception as e:
    print(f"\n❌ Error al extraer el code: {e}")
    print("Asegúrate de copiar la URL completa que comienza con:")
    print("https://localhost/callback?code=...")
    exit(1)

# ============================================
# 🎫 PASO 2: INTERCAMBIAR CODE POR ACCESS TOKEN
# ============================================
print("=" * 60)
print("🔄 PASO 2: OBTENIENDO ACCESS TOKEN")
print("=" * 60)

token_url = "https://open.tiktokapis.com/v2/oauth/token/"

token_data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": code,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI,
    "code_verifier": code_verifier  # 🔥 IMPORTANTE: Enviamos el verifier
}

try:
    response = httpx.post(token_url, data=token_data, timeout=30.0)
    response.raise_for_status()
    token_response = response.json()
    
    if "access_token" in token_response:
        print("\n🎉 ¡ACCESS TOKEN OBTENIDO EXITOSAMENTE!\n")
        print("=" * 60)
        print("📝 GUARDA ESTOS VALORES EN TU ARCHIVO .env")
        print("=" * 60)
        print(f"\nTIKTOK_CLIENT_KEY={CLIENT_KEY}")
        print(f"TIKTOK_CLIENT_SECRET={CLIENT_SECRET}")
        print(f"TIKTOK_ACCESS_TOKEN={token_response['access_token']}")
        print(f"TIKTOK_REFRESH_TOKEN={token_response.get('refresh_token', 'N/A')}")
        print(f"\n⏰ El token expira en: {token_response['expires_in']} segundos ({token_response['expires_in']//3600} horas)")
        print("\n✅ Copia y pega estas líneas en tu archivo backend/.env")
        
    else:
        print("\n❌ No se recibió access_token en la respuesta:")
        print(token_response)
        
except httpx.HTTPStatusError as e:
    print(f"\n❌ Error HTTP {e.response.status_code}:")
    print(e.response.text)
    print("\n💡 Posibles causas:")
    print("   - CLIENT_SECRET incorrecto")
    print("   - El code ya fue usado (intenta de nuevo desde el paso 1)")
    print("   - Code_verifier no coincide con code_challenge")
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")

print("\n" + "=" * 60)