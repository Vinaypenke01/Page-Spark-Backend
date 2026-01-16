import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_generate():
    print("Testing Generation...")
    url = f"{BASE_URL}/api/generate/"
    payload = {
        "email": "test@example.com",
        "prompt": "A simple colorful landing page for a party planner.",
        "page_type": "landing",
        "theme": "colorful"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 201:
            data = response.json()
            print("SUCCESS: Page Generated")
            print(f"ID: {data.get('id')}")
            print(f"URL: {data.get('live_url')}")
            return data.get('id')
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_live_page(page_id):
    if not page_id:
        return
    print(f"\nTesting Live Page Fetch for {page_id}...")
    url = f"{BASE_URL}/p/{page_id}/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("SUCCESS: Live Page Retrieved")
            print(f"Content Length: {len(response.text)}")
            if "Example Domain" in response.text or "html" in response.text.lower(): # Basic check
                 print("Content looks like HTML")
        else:
            print(f"FAILED: {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")

def test_history():
    print("\nTesting History...")
    url = f"{BASE_URL}/api/history/?email=test@example.com"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: History Retrieved. Count: {len(data)}")
        else:
            print(f"FAILED: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    page_id = test_generate()
    if page_id:
        test_live_page(page_id)
        test_history()
