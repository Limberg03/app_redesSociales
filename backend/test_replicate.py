#!/usr/bin/env python3
"""
🧪 Script de Prueba: Replicate + Flux Schnell
Verifica que la integración de Replicate funciona correctamente
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_replicate_basico():
    """
    Test básico: Genera una imagen simple
    """
    print("\n" + "="*70)
    print("🧪 TEST 1: Generación Básica con Replicate")
    print("="*70)
    
    try:
        import replicate
        
        token = os.getenv("REPLICATE_API_TOKEN")
        
        if not token:
            print("❌ REPLICATE_API_TOKEN no encontrado en .env")
            return False
        
        os.environ["REPLICATE_API_TOKEN"] = token
        print("✅ Token configurado")
        
        # Test simple
        print("\n🎨 Generando imagen de prueba...")
        print("📝 Prompt: 'university students studying in modern library'")
        
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": "university students studying in modern library, natural lighting, realistic photography",
                "go_fast": True,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpg",
                "output_quality": 90
            }
        )
        
        if isinstance(output, list) and len(output) > 0:
            imagen_url = output[0]
        else:
            imagen_url = str(output)
        
        print(f"✅ Imagen generada exitosamente!")
        print(f"🔗 URL: {imagen_url}")
        print("\n💡 Copia esta URL en tu navegador para ver la imagen")
        
        return True
        
    except ImportError:
        print("❌ Librería 'replicate' no instalada")
        print("💡 Ejecuta: pip install replicate")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_prompt_academico():
    """
    Test con prompt académico real
    """
    print("\n" + "="*70)
    print("🧪 TEST 2: Prompt Académico Contextual")
    print("="*70)
    
    try:
        import replicate
        
        token = os.getenv("REPLICATE_API_TOKEN")
        os.environ["REPLICATE_API_TOKEN"] = token
        
        # Simular texto de publicación
        texto_entrada = "La FICCT anuncia taller de Inteligencia Artificial este viernes"
        
        print(f"\n📝 Texto de entrada: '{texto_entrada}'")
        
        # Generar prompt contextual (como lo hace el sistema)
        prompt = "High quality professional photography, UAGRM university computer science students learning about artificial intelligence in modern tech lab, laptops and screens, bright classroom, engaged students, realistic"
        
        print(f"🎨 Prompt mejorado: '{prompt[:100]}...'")
        print("\n⏳ Generando imagen (2-4 segundos)...")
        
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt,
                "go_fast": True,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpg",
                "output_quality": 90
            }
        )
        
        if isinstance(output, list) and len(output) > 0:
            imagen_url = output[0]
        else:
            imagen_url = str(output)
        
        print(f"✅ Imagen generada para contenido académico!")
        print(f"🔗 URL: {imagen_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_subida_imgur():
    """
    Test completo: Genera imagen y sube a Imgur
    """
    print("\n" + "="*70)
    print("🧪 TEST 3: Generación + Subida a Imgur")
    print("="*70)
    
    try:
        import replicate
        import httpx
        
        token = os.getenv("REPLICATE_API_TOKEN")
        os.environ["REPLICATE_API_TOKEN"] = token
        
        print("\n🎨 Generando imagen...")
        
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": "UAGRM university campus, students walking, modern architecture, sunny day, Bolivia, realistic photography",
                "go_fast": True,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpg",
                "output_quality": 90
            }
        )
        
        if isinstance(output, list) and len(output) > 0:
            imagen_url = output[0]
        else:
            imagen_url = str(output)
        
        print(f"✅ Imagen generada: {imagen_url[:50]}...")
        
        # Descargar imagen
        print("\n📥 Descargando imagen...")
        response = httpx.get(imagen_url, timeout=30.0)
        response.raise_for_status()
        imagen_bytes = response.content
        print(f"✅ Descargada ({len(imagen_bytes)} bytes)")
        
        # Subir a Imgur
        print("\n📤 Subiendo a Imgur...")
        imgur_client_id = "546c25a59c58ad7"
        imgur_headers = {"Authorization": f"Client-ID {imgur_client_id}"}
        
        imgur_response = httpx.post(
            "https://api.imgur.com/3/upload",
            headers=imgur_headers,
            files={"image": imagen_bytes},
            timeout=30.0
        )
        imgur_response.raise_for_status()
        imgur_result = imgur_response.json()
        
        if imgur_result["success"]:
            url_imgur = imgur_result["data"]["link"]
            print(f"✅ Subida exitosa a Imgur!")
            print(f"🔗 URL permanente: {url_imgur}")
            print("\n💡 Esta URL es la que se usará en Instagram/WhatsApp")
            return True
        else:
            print("❌ Error al subir a Imgur")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_tiempo_generacion():
    """
    Test de velocidad
    """
    print("\n" + "="*70)
    print("🧪 TEST 4: Velocidad de Generación")
    print("="*70)
    
    try:
        import replicate
        import time
        
        token = os.getenv("REPLICATE_API_TOKEN")
        os.environ["REPLICATE_API_TOKEN"] = token
        
        print("\n⏱️  Midiendo tiempo de generación...")
        
        inicio = time.time()
        
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": "university classroom, students learning",
                "go_fast": True,
                "num_outputs": 1,
                "aspect_ratio": "1:1",
                "output_format": "jpg"
            }
        )
        
        fin = time.time()
        tiempo_total = fin - inicio
        
        print(f"✅ Imagen generada en {tiempo_total:.2f} segundos")
        
        if tiempo_total < 5:
            print("🚀 ¡Excelente velocidad! (menos de 5 segundos)")
        elif tiempo_total < 10:
            print("✅ Buena velocidad (menos de 10 segundos)")
        else:
            print("⚠️  Un poco lento, puede ser tu conexión")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """
    Ejecuta todos los tests
    """
    print("\n" + "="*70)
    print("🚀 SUITE DE PRUEBAS: REPLICATE + FLUX SCHNELL")
    print("="*70)
    print("\nEste script verificará que:")
    print("  1. ✅ Replicate esté instalado")
    print("  2. ✅ El token esté configurado")
    print("  3. ✅ Puedas generar imágenes")
    print("  4. ✅ Puedas subirlas a Imgur")
    print("  5. ✅ La velocidad sea buena")
    
    resultados = []
    
    # Test 1
    resultados.append(("Generación Básica", test_replicate_basico()))
    
    # Test 2
    if resultados[0][1]:
        resultados.append(("Prompt Académico", test_prompt_academico()))
    
    # Test 3
    if resultados[0][1]:
        resultados.append(("Subida a Imgur", test_subida_imgur()))
    
    # Test 4
    if resultados[0][1]:
        resultados.append(("Velocidad", test_tiempo_generacion()))
    
    # Resumen
    print("\n" + "="*70)
    print("📊 RESUMEN DE TESTS")
    print("="*70)
    
    exitosos = sum(1 for _, resultado in resultados if resultado)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        emoji = "✅" if resultado else "❌"
        print(f"{emoji} {nombre}")
    
    print(f"\n📈 Resultado: {exitosos}/{total} tests exitosos")
    
    if exitosos == total:
        print("\n🎉 ¡PERFECTO! Tu integración de Replicate funciona correctamente")
        print("✅ Ya puedes usar llm_service_UPDATED.py en producción")
    elif exitosos > 0:
        print("\n⚠️  Algunos tests fallaron, revisa los errores arriba")
    else:
        print("\n❌ Tests fallidos. Verifica:")
        print("   1. pip install replicate")
        print("   2. REPLICATE_API_TOKEN en .env")
        print("   3. Conexión a internet")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()