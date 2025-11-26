import requests
import sys

BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api/chat"
AUTH_URL = f"{BASE_URL}/token"

# Test credentials (ensure these exist or use a known user)
USERNAME = "testuser"
PASSWORD = "testpassword"

def get_token():
    try:
        response = requests.post(AUTH_URL, data={"username": USERNAME, "password": PASSWORD})
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Failed to get token: {response.text}")
            # Try registering if login fails
            register_url = f"{BASE_URL}/users/"
            reg_response = requests.post(register_url, json={"username": USERNAME, "email": "test@example.com", "password": PASSWORD})
            if reg_response.status_code == 200:
                print("Registered new user.")
                return get_token()
            else:
                print(f"Failed to register: {reg_response.text}")
                return None
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        return None

def test_create_conversation(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_URL}/conversations", headers=headers, json={"title": "Test Chat"})
    if response.status_code == 200:
        print("Create Conversation: SUCCESS")
        return response.json()["id"]
    else:
        print(f"Create Conversation: FAILED - {response.text}")
        return None

def test_send_message(token, conversation_id):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"role": "user", "content": "Hello, this is a test message."}
    response = requests.post(f"{API_URL}/conversations/{conversation_id}/messages", headers=headers, json=data)
    if response.status_code == 200:
        print("Send Message: SUCCESS")
        return True
    else:
        print(f"Send Message: FAILED - {response.text}")
        return False

def test_get_history(token, conversation_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/conversations/{conversation_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        if len(data["messages"]) > 0:
            print("Get History: SUCCESS")
            return True
        else:
            print("Get History: FAILED - No messages found")
            return False
    else:
        print(f"Get History: FAILED - {response.text}")
        return False

def main():
    print("Starting Chat API Tests...")
    token = get_token()
    if not token:
        print("Aborting tests due to auth failure.")
        return

    conv_id = test_create_conversation(token)
    if conv_id:
        if test_send_message(token, conv_id):
            test_get_history(token, conv_id)

if __name__ == "__main__":
    main()
