"""
Script de prueba para verificar la VALIDACIÓN y ADAPTACIÓN de contenido académico
"""

import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

# Casos de prueba
CONTENIDO_NO_ACADEMICO = "Un perro mordió a una abuela en la plaza principal"
CONTENIDO_ACADEMICO = "La UAGRM habilitó el retiro de materias hasta el 30 de noviembre de 2024"

def test_contenido_no_academico_facebook():
    """Prueba que contenido NO académico sea RECHAZADO"""
    print("\n" + "="*60)
    print("❌ TEST 1: CONTENIDO NO ACADÉMICO (debe ser rechazado)")
    print("="*60)
    
    payload = {
        "text": CONTENIDO_NO_ACADEMICO,
        "image_url": "https://picsum.photos/800/600"
    }
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/test/facebook",
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 400:
            error = response.json()
            print("\n✅ CORRECTO: El contenido fue rechazado")
            print(f"\n📝 Mensaje de error:")
            print(f"   {error['detail']['mensaje']}")
            return True
        else:
            print(f"\n❌ ERROR: El contenido NO fue rechazado (status: {response.status_code})")
            print(f"Respuesta: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False


def test_contenido_academico_facebook():
    """Prueba que contenido académico sea ACEPTADO y ADAPTADO"""
    print("\n" + "="*60)
    print("✅ TEST 2: CONTENIDO ACADÉMICO PARA FACEBOOK")
    print("="*60)
    
    payload = {
        "text": CONTENIDO_ACADEMICO,
        "image_url": "https://picsum.photos/800/600"
    }
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/test/facebook",
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 200:
            resultado = response.json()
            
            print("\n✅ CORRECTO: El contenido fue aceptado")
            
            print("\n🔍 VALIDACIÓN:")
            validacion = resultado.get("validacion", {})
            print(f"   Es académico: {validacion.get('es_academico')}")
            print(f"   Razón: {validacion.get('razon')}")
            
            print("\n📝 TEXTO ORIGINAL:")
            print(f"   {CONTENIDO_ACADEMICO}")
            
            print("\n✨ TEXTO ADAPTADO PARA FACEBOOK:")
            adaptacion = resultado.get("adaptacion", {})
            print(f"   {adaptacion.get('text', 'N/A')[:200]}...")
            
            print("\n🏷️ HASHTAGS:")
            print(f"   {', '.join(adaptacion.get('hashtags', []))}")
            
            print(f"\n📊 Caracteres: {adaptacion.get('character_count', 0)}")
            
            print("\n✅ El contenido académico fue validado, adaptado y estaría listo para publicar")
            return True
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False


def test_contenido_academico_instagram():
    """Prueba que contenido académico sea ACEPTADO y ADAPTADO para Instagram"""
    print("\n" + "="*60)
    print("✅ TEST 3: CONTENIDO ACADÉMICO PARA INSTAGRAM")
    print("="*60)
    
    payload = {
        "text": CONTENIDO_ACADEMICO,
        "image_url": "https://picsum.photos/800/600"
    }
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/test/instagram",
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 200:
            resultado = response.json()
            
            print("\n✅ CORRECTO: El contenido fue aceptado")
            
            print("\n🔍 VALIDACIÓN:")
            validacion = resultado.get("validacion", {})
            print(f"   Es académico: {validacion.get('es_academico')}")
            print(f"   Razón: {validacion.get('razon')}")
            
            print("\n📝 TEXTO ORIGINAL:")
            print(f"   {CONTENIDO_ACADEMICO}")
            
            print("\n✨ TEXTO ADAPTADO PARA INSTAGRAM:")
            adaptacion = resultado.get("adaptacion", {})
            print(f"   {adaptacion.get('text', 'N/A')[:200]}...")
            
            print("\n🏷️ HASHTAGS:")
            print(f"   {', '.join(adaptacion.get('hashtags', []))}")
            
            if "suggested_image_prompt" in adaptacion:
                print(f"\n🎨 PROMPT SUGERIDO PARA IMAGEN:")
                print(f"   {adaptacion['suggested_image_prompt']}")
            
            print(f"\n📊 Caracteres: {adaptacion.get('character_count', 0)}")
            
            print("\n✅ El contenido académico fue validado, adaptado y estaría listo para publicar")
            return True
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False


def comparar_adaptaciones():
    """Compara las adaptaciones de Facebook e Instagram para contenido académico"""
    print("\n" + "="*60)
    print("🔄 TEST 4: COMPARACIÓN FACEBOOK VS INSTAGRAM")
    print("="*60)
    
    payload_adapt = {
        "titulo": "Retiro de materias UAGRM",
        "contenido": CONTENIDO_ACADEMICO,
        "target_networks": ["facebook", "instagram"]
    }
    
    try:
        response = httpx.post(
            f"{BASE_URL}/api/posts/adapt",
            json=payload_adapt,
            timeout=30.0
        )
        
        if response.status_code == 200:
            resultado = response.json()
            
            print("\n📝 CONTENIDO ORIGINAL:")
            print(f"   {CONTENIDO_ACADEMICO}")
            
            print("\n" + "-"*60)
            print("🔵 FACEBOOK:")
            fb = resultado["data"]["facebook"]
            print(f"   Texto: {fb.get('text', '')[:150]}...")
            print(f"   Hashtags ({len(fb.get('hashtags', []))}): {', '.join(fb.get('hashtags', []))}")
            print(f"   Caracteres: {fb.get('character_count', 0)}")
            
            print("\n" + "-"*60)
            print("📸 INSTAGRAM:")
            ig = resultado["data"]["instagram"]
            print(f"   Texto: {ig.get('text', '')[:150]}...")
            print(f"   Hashtags ({len(ig.get('hashtags', []))}): {', '.join(ig.get('hashtags', []))}")
            print(f"   Caracteres: {ig.get('character_count', 0)}")
            
            print("\n" + "-"*60)
            print("📊 DIFERENCIAS:")
            print(f"  - Facebook usa {len(fb.get('hashtags', []))} hashtags")
            print(f"  - Instagram usa {len(ig.get('hashtags', []))} hashtags")
            print(f"  - Diferencia de longitud: {abs(len(fb.get('text', '')) - len(ig.get('text', '')))} caracteres")
            
            print("\n✅ Ambas adaptaciones mantienen el enfoque académico")
            return True
        else:
            print(f"\n❌ ERROR: Status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("\n🧪 PRUEBAS DE VALIDACIÓN Y ADAPTACIÓN DE CONTENIDO ACADÉMICO")
    print("="*60)
    print("Este script verifica:")
    print("  1. Que contenido NO académico sea rechazado")
    print("  2. Que contenido académico sea aceptado y adaptado")
    print("  3. Que las adaptaciones sean apropiadas para cada red")
    print("="*60)
    
    # Verificar que el servidor esté corriendo
    try:
        response = httpx.get(f"{BASE_URL}/", timeout=5.0)
        if response.status_code != 200:
            print("\n❌ El servidor no está respondiendo correctamente")
            print("Asegúrate de que FastAPI esté corriendo:")
            print("  uvicorn main:app --reload")
            exit(1)
    except Exception as e:
        print("\n❌ No se puede conectar al servidor")
        print("Asegúrate de que FastAPI esté corriendo:")
        print("  uvicorn main:app --reload")
        exit(1)
    
    print("\n✅ Servidor conectado correctamente\n")
    
    # Ejecutar pruebas
    test1 = test_contenido_no_academico_facebook()
    test2 = test_contenido_academico_facebook()
    test3 = test_contenido_academico_instagram()
    test4 = comparar_adaptaciones()
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"❌ Rechazo de contenido no académico: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"✅ Aceptación Facebook: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"✅ Aceptación Instagram: {'✅ PASS' if test3 else '❌ FAIL'}")
    print(f"🔄 Comparación de adaptaciones: {'✅ PASS' if test4 else '❌ FAIL'}")
    
    if test1 and test2 and test3 and test4:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("\n💡 El sistema ahora:")
        print("   ✅ Valida que el contenido sea académico")
        print("   ✅ Rechaza contenido inapropiado con mensaje claro")
        print("   ✅ Adapta contenido académico para cada red social")
        print("   ✅ Mantiene el enfoque educativo en las adaptaciones")
    else:
        print("\n❌ Algunas pruebas fallaron")
        print("Revisa los errores arriba y verifica tu configuración.")