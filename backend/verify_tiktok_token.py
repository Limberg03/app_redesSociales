
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TIKTOK_ACCESS_TOKEN")
print(f"Token in env: {token}")

if not token:
    print("❌ No token found in environment")
    exit(1)

url = "https://open.tiktokapis.com/v2/user/info/?fields=open_id,union_id,avatar_url"
headers = {
    "Authorization": f"Bearer {token}",
}

print(f"Testing token against: {url}")

try:
    response = httpx.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
