#!/usr/bin/env python3
"""
🔍 Verificador de Token de TikTok
Verifica el estado actual del token y muestra información de expiración
"""

import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# ============================================
# 🔧 CONFIGURACIÓN
# ============================================
ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")

if not ACCESS_TOKEN:
    print("❌ Error: TIKTOK_ACCESS_TOKEN no encontrado en .env")
    exit(1)

print("="*70)
print("🔍 VERIFICADOR DE TOKEN DE TIKTOK")
print("="*70)

# ============================================
# 📊 INFORMACIÓN DEL TOKEN
# ============================================
print(f"\n📝 Token actual (primeros 20 caracteres):")
print(f"   {ACCESS_TOKEN[:20]}...")

# ============================================
# ✅ VERIFICAR VALIDEZ DEL TOKEN
# ============================================
print("\n🔄 Verificando validez del token...")

# Intentamos hacer una llamada simple a la API de TikTok
# Usamos el endpoint de información del usuario
test_url = "https://open.tiktokapis.com/v2/user/info/"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "fields": ["open_id", "union_id", "avatar_url", "display_name"]
}

try:
    response = httpx.post(test_url, json=payload, headers=headers, timeout=10.0)
    
    if response.status_code == 200:
        user_data = response.json()
        
        print("\n✅ TOKEN VÁLIDO")
        print("="*70)
        
        if "data" in user_data and "user" in user_data["data"]:
            user = user_data["data"]["user"]
            print(f"\n👤 Usuario: {user.get('display_name', 'N/A')}")
            print(f"🆔 Open ID: {user.get('open_id', 'N/A')[:15]}...")
        
        print("\n⚠️  NOTA IMPORTANTE:")
        print("   La API de TikTok NO devuelve directamente la fecha de expiración")
        print("   en las respuestas. Debemos calcularla basándonos en cuándo")
        print("   obtuviste el token.")
        
    elif response.status_code == 401:
        error_data = response.json()
        error_code = error_data.get("error", {}).get("code", "")
        error_msg = error_data.get("error", {}).get("message", "")
        
        print("\n❌ TOKEN INVÁLIDO O EXPIRADO")
        print("="*70)
        print(f"\n🔴 Error: {error_code}")
        print(f"📝 Mensaje: {error_msg}")
        
        if "expired" in error_msg.lower() or error_code == "access_token_invalid":
            print("\n💡 SOLUCIÓN:")
            print("   1. Ejecuta: python refresh_tiktok_token.py")
            print("   2. O genera un nuevo token: python get_token_manual.py")
        
    else:
        print(f"\n⚠️  Respuesta inesperada: HTTP {response.status_code}")
        print(f"📝 Respuesta: {response.text[:200]}")
        
except httpx.RequestError as e:
    print(f"\n❌ Error de conexión: {e}")
    print("   Verifica tu conexión a internet")
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")

# ============================================
# ⏰ INFORMACIÓN SOBRE EXPIRACIÓN
# ============================================
print("\n" + "="*70)
print("⏰ INFORMACIÓN SOBRE EXPIRACIÓN DE TOKENS")
print("="*70)

print("""
📌 Los tokens de TikTok tienen estas características:

1️⃣  ACCESS TOKEN:
   • Duración: 24 HORAS desde su generación
   • Uso: Para hacer publicaciones y llamadas a la API
   • Se puede refrescar con el REFRESH_TOKEN

2️⃣  REFRESH TOKEN:
   • Duración: 1 AÑO desde su generación
   • Uso: Para obtener un nuevo ACCESS_TOKEN
   • NO expira mientras lo uses al menos 1 vez al año

🔄 PROCESO DE REFRESCO:
   1. Antes de que pasen 24 horas, ejecuta: python refresh_tiktok_token.py
   2. El script te dará un NUEVO access_token
   3. Actualiza tu .env con el nuevo token
   4. El refresh_token también se actualiza (1 año más de vida)

💡 RECOMENDACIONES:
   • Refresca el token cada 12 horas (para estar seguro)
   • Guarda el refresh_token - es MÁS IMPORTANTE que el access_token
   • Si el refresh_token expira, tendrás que autorizar de nuevo (get_token_manual.py)
""")

# ============================================
# 🔄 ¿NECESITAS REFRESCAR?
# ============================================
print("="*70)
print("🔄 ¿NECESITAS REFRESCAR EL TOKEN?")
print("="*70)

respuesta = input("\n¿Cuántas horas hace que generaste este token? (0-24): ").strip()

try:
    horas = int(respuesta)
    
    if horas >= 24:
        print("\n🔴 URGENTE: Tu token ya expiró")
        print("   Ejecuta: python refresh_tiktok_token.py")
    elif horas >= 20:
        print("\n🟡 ADVERTENCIA: Tu token está por expirar pronto")
        print("   Te quedan aproximadamente", 24 - horas, "horas")
        print("   Refresca el token ahora: python refresh_tiktok_token.py")
    elif horas >= 12:
        print("\n🟢 Token válido, pero considera refrescarlo pronto")
        print("   Te quedan aproximadamente", 24 - horas, "horas")
        print("   Puedes refrescar en cualquier momento: python refresh_tiktok_token.py")
    else:
        print("\n✅ Token recién generado, deberías estar bien")
        print("   Te quedan aproximadamente", 24 - horas, "horas")
        print("   Refresca antes de que pasen 24 horas")
    
except ValueError:
    print("\n⚠️  Entrada inválida")

print("\n" + "="*70)
print("✅ Verificación completada")
print("="*70)