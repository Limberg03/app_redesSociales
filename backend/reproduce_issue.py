
import os
import sys
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load env vars
load_dotenv()

try:
    import llm_service
except ImportError:
    # If running from backend dir directly
    import llm_service

def test_keywords():
    texto = "la navidad llega a la FICCT"
    print(f"Testing with text: '{texto}'")
    
    try:
        keywords = llm_service.extraer_keywords_con_llm(texto)
        print("\nGenerated Keywords:")
        for k in keywords:
            print(f"- {k}")
            
        # Also test fallback logic just in case
        print("\nFallback Logic Check:")
        fallback = llm_service.generar_keywords_fallback(texto)
        for k in fallback:
            print(f"- {k}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_keywords()
