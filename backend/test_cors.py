import requests

url = "http://127.0.0.1:8000/api/auth/login"
headers = {
    "Origin": "http://localhost:5173",
    "Access-Control-Request-Method": "POST",
    "Access-Control-Request-Headers": "content-type"
}

try:
    response = requests.options(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
