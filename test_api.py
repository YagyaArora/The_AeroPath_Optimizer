import requests

url = "https://api.flightapi.io/onewaytrip/6827a8a12fdd3d93898cfeeb/DEL/BOM/2025-06-17/1/0/0/Economy/INR"

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print("Response Headers:")
    for key, value in response.headers.items():
        print(f"{key}: {value}")
    print("\nResponse Content:")
    print(response.text)
except Exception as e:
    print(f"Error: {str(e)}")
