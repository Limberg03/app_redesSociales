#!/usr/bin/env python3
"""
🔄 Refrescador de Token de TikTok - Versión Mejorada
Refresca tu access_token usando el refresh_token
"""

import httpx
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("TIKTOK_REFRESH_TOKEN")

print("="*70)
print("🔄 REFRESCANDO TOKEN DE TIKTOK")
print("="*70)

# ============================================
# ✅ VALIDAR CONFIGURACIÓN
# ============================================
errores = []

if not CLIENT_KEY:
    errores.append("❌ TIKTOK_CLIENT_KEY no encontrado en .env")
if not CLIENT_SECRET:
    errores.append("❌ TIKTOK_CLIENT_SECRET no encontrado en .env")
if not REFRESH_TOKEN:
    errores.append("❌ TIKTOK_REFRESH_TOKEN no encontrado en .env")

if errores:
    print("\n⚠️  ERRORES DE CONFIGURACIÓN:\n")
    for error in errores:
        print(f"   {error}")
    print("\n💡 Asegúrate de tener todas las variables en tu .env")
    exit(1)

print("\n✅ Configuración válida")
print(f"   Client Key: {CLIENT_KEY[:15]}...")
print(f"   Refresh Token: {REFRESH_TOKEN[:20]}...")

# ============================================
# 🔄 REFRESCAR TOKEN
# ============================================
print("\n🔄 Enviando solicitud a TikTok...")

url = "https://open.tiktokapis.com/v2/oauth/token/"

data = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN
}

try:
    response = httpx.post(url, data=data, timeout=30.0)
    
    if response.status_code == 200:
        result = response.json()
        
        nuevo_access_token = result.get("access_token")
        nuevo_refresh_token = result.get("refresh_token")
        expires_in = result.get("expires_in", 86400)
        
        horas_expiracion = expires_in // 3600
        
        # Calcular fecha de expiración aproximada
        ahora = datetime.now()
        expira_en = ahora + timedelta(seconds=expires_in)
        
        print("\n" + "="*70)
        print("🎉 ¡TOKEN REFRESCADO EXITOSAMENTE!")
        print("="*70)
        
        print("\n📝 ACTUALIZA TU ARCHIVO .env CON ESTOS VALORES:")
        print("-"*70)
        print(f"\nTIKTOK_CLIENT_KEY={CLIENT_KEY}")
        print(f"TIKTOK_CLIENT_SECRET={CLIENT_SECRET}")
        print(f"TIKTOK_ACCESS_TOKEN={nuevo_access_token}")
        print(f"TIKTOK_REFRESH_TOKEN={nuevo_refresh_token}")
        
        print("\n" + "="*70)
        print("⏰ INFORMACIÓN DE EXPIRACIÓN")
        print("="*70)
        print(f"\n🕐 Fecha actual: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏰ Expira en: {horas_expiracion} horas ({expires_in} segundos)")
        print(f"📅 Fecha de expiración: {expira_en.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "="*70)
        print("💡 IMPORTANTE")
        print("="*70)
        print("""
1️⃣  COPIA Y PEGA las líneas de arriba en tu archivo backend/.env
   
2️⃣  El ACCESS_TOKEN dura 24 HORAS
   • Refresca el token antes de que expire (recomendado: cada 12 horas)
   • Ejecuta este script de nuevo: python refresh_tiktok_token.py
   
3️⃣  El REFRESH_TOKEN dura 1 AÑO
   • Se actualiza automáticamente cada vez que refrescas el access_token
   • Si el refresh_token expira, tendrás que autorizar de nuevo la app
   
4️⃣  GUARDA AMBOS TOKENS en tu .env inmediatamente
""")
        
        # ============================================
        # 📊 COMPARACIÓN DE TOKENS
        # ============================================
        print("="*70)
        print("🔍 COMPARACIÓN DE TOKENS")
        print("="*70)
        
        print("\n🔴 ACCESS TOKEN ANTERIOR:")
        print(f"   {os.getenv('TIKTOK_ACCESS_TOKEN', 'N/A')[:30]}...")
        print("\n🟢 ACCESS TOKEN NUEVO:")
        print(f"   {nuevo_access_token[:30]}...")
        
        if os.getenv('TIKTOK_ACCESS_TOKEN') == nuevo_access_token:
            print("\n⚠️  ADVERTENCIA: El token es el mismo")
            print("   Esto puede significar que:")
            print("   • Ya refrescaste el token recientemente")
            print("   • TikTok reutilizó el mismo token (poco común)")
        else:
            print("\n✅ Token actualizado correctamente (es diferente)")
        
        print("\n🔴 REFRESH TOKEN ANTERIOR:")
        print(f"   {REFRESH_TOKEN[:30]}...")
        print("\n🟢 REFRESH TOKEN NUEVO:")
        print(f"   {nuevo_refresh_token[:30]}...")
        
        if REFRESH_TOKEN == nuevo_refresh_token:
            print("\n⚠️  El refresh_token es el mismo (esto es normal)")
        else:
            print("\n✅ Refresh token también actualizado")
        
        print("\n" + "="*70)
        print("🚀 PRÓXIMOS PASOS")
        print("="*70)
        print("""
1. Abre tu archivo backend/.env
2. Reemplaza las líneas de TIKTOK_ACCESS_TOKEN y TIKTOK_REFRESH_TOKEN
3. Guarda el archivo
4. Reinicia tu servidor backend si está corriendo
5. ¡Listo! Puedes seguir publicando en TikTok

⏰ RECUERDA: Refresca el token nuevamente antes de que pasen 24 horas
""")
        
    elif response.status_code == 400:
        error_data = response.json()
        error_code = error_data.get("error", {}).get("code", "")
        error_msg = error_data.get("error", {}).get("message", "")
        
        print("\n" + "="*70)
        print("❌ ERROR AL REFRESCAR TOKEN")
        print("="*70)
        print(f"\n🔴 Código de error: {error_code}")
        print(f"📝 Mensaje: {error_msg}")
        
        if "refresh_token_invalid" in error_code or "expired" in error_msg.lower():
            print("\n💡 SOLUCIÓN:")
            print("""
Tu REFRESH_TOKEN ha expirado o es inválido.
Necesitas generar uno nuevo:

1. Ejecuta: python get_token_manual.py
2. Sigue el proceso de autorización
3. Copia los nuevos tokens a tu .env
4. El refresh_token durará 1 año más
""")
        else:
            print("\n💡 POSIBLES CAUSAS:")
            print("   • CLIENT_SECRET incorrecto")
            print("   • REFRESH_TOKEN ya usado o expirado")
            print("   • Problema de red con TikTok API")
            print("\nIntenta generar nuevos tokens: python get_token_manual.py")
        
    else:
        print(f"\n❌ Error HTTP {response.status_code}:")
        print(response.text)
        
except httpx.RequestError as e:
    print(f"\n❌ Error de conexión: {e}")
    print("   Verifica tu conexión a internet")
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")

print("\n" + "="*70)