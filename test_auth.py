import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
BASE_URL = "http://localhost:5000/api/auth"
TEST_USER = {
    "name": "Test User",
    "email": f"test{os.urandom(4).hex()}@example.com",
    "mobile": f"9{os.urandom(8).hex()[:8]}",
    "password": "Test@123"
}

def print_response(response, description):
    """Print formatted response"""
    print(f"\n{description}:")
    print(f"Status Code: {response.status_code}")
    try:
        print("Response:", json.dumps(response.json(), indent=2))
    except:
        print("Response:", response.text)

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    url = f"{BASE_URL}/register"
    response = requests.post(url, json=TEST_USER)
    print_response(response, "Registration Response")
    return response.json() if response.status_code == 201 else None

def test_login():
    """Test user login"""
    print("\n=== Testing User Login ===")
    url = f"{BASE_URL}/login"
    login_data = {
        "identifier": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    response = requests.post(url, json=login_data)
    print_response(response, "Login Response")
    return response.json() if response.status_code == 200 else None

def test_invalid_login():
    """Test login with invalid credentials"""
    print("\n=== Testing Invalid Login ===")
    url = f"{BASE_URL}/login"
    login_data = {
        "identifier": TEST_USER["email"],
        "password": "wrongpassword"
    }
    response = requests.post(url, json=login_data)
    print_response(response, "Invalid Login Response")

def test_get_profile(access_token):
    """Test getting user profile with valid token"""
    print("\n=== Testing Get Profile ===")
    url = f"{BASE_URL}/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    print_response(response, "Profile Response")

def test_invalid_token():
    """Test getting user profile with invalid token"""
    print("\n=== Testing Invalid Token ===")
    url = f"{BASE_URL}/me"
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = requests.get(url, headers=headers)
    print_response(response, "Invalid Token Response")

if __name__ == "__main__":
    print("=== Starting Authentication API Tests ===")
    
    # Run tests
    test_register()
    login_response = test_login()
    
    if login_response and 'access_token' in login_response:
        access_token = login_response['access_token']
        test_get_profile(access_token)
    
    test_invalid_login()
    test_invalid_token()
    
    print("\n=== Authentication API Tests Complete ===")
