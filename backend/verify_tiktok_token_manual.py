import os
import httpx
from dotenv import load_dotenv

# Force reload of .env
load_dotenv(override=True)

TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN")

print(f"Checking token: {TOKEN[:10]}...{TOKEN[-5:] if TOKEN else 'None'}")

if not TOKEN:
    print("No token found in .env")
    exit(1)

url = "https://open.tiktokapis.com/v2/user/info/"
headers = {
    "Authorization": f"Bearer {TOKEN}"
}
params = {
    "fields": "open_id,union_id,avatar_url,display_name"
}

try:
    print(f"Sending request to {url}...")
    response = httpx.get(url, headers=headers, params=params)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if "data" in data and "error" not in data:
            print("Token is VALID!")
            print(f"User: {data['data'].get('display_name')}")
        else:
            print("Token seems invalid or scope issue.")
    else:
        print("Token rejected.")

except Exception as e:
    print(f"Error: {e}")
