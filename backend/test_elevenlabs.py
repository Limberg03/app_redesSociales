# test_elevenlabs.py
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "onwK4e9ZLuTAKqWW03F9"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": API_KEY
}

data = {
    "text": "Hola, esto es una prueba",
    "model_id": "eleven_multilingual_v2"
}

response = httpx.post(url, json=data, headers=headers, timeout=30.0)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

if response.status_code == 200:
    print("✅ API Key funciona correctamente")
    with open("test_audio.mp3", "wb") as f:
        f.write(response.content)
    print("✅ Audio guardado en test_audio.mp3")
else:
    print("❌ Error:")
    print(response.json())