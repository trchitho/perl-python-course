"""Test API call directly"""
import requests
import json

url = "http://localhost:5000/api/auth/forgot-password"
data = {"email": "thien64tb@gmail.com"}

print(f"Sending POST to {url}")
print(f"Data: {data}")
print("-" * 60)

try:
    response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print("-" * 60)
    print("Response Body:")
    print(response.text[:500])  # First 500 chars
    print("-" * 60)
    
    if response.headers.get('content-type', '').startswith('application/json'):
        print("JSON Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("⚠️ Response is not JSON!")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
