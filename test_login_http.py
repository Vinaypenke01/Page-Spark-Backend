import requests
import json

BASE_URL = "http://localhost:8000/api/auth/login/"

def test_login(username, password):
    print(f"Testing login for {username}...")
    try:
        response = requests.post(BASE_URL, json={'username': username, 'password': password})
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(response.json().keys())
        else:
            print("Failed!")
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Ensure user exists (assuming debug_auth.py ran or previous browser usage created 'subagent_final')
    # If not, this might fail. Ideally, I should create user via register first.
    
    # Try with 'subagent_final' / 'FinalPassword123!'
    test_login('subagent_final', 'FinalPassword123!')
    
    # Try with email 'final@example.com'
    test_login('final@example.com', 'FinalPassword123!')
