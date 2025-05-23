import requests
import json
from datetime import datetime, timedelta

def test_amadeus():
    # API configuration
    base_url = "https://test.api.amadeus.com"
    api_key = "BqDtPNTcgYsPP0X88iGrEsG3IMNzRpoS"
    api_secret = "cr0APVNsSEoceqUt"

    # Get access token
    token_response = requests.post(
        f"{base_url}/v1/security/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": api_secret
        }
    )
    
    print("Token Response:", json.dumps(token_response.json(), indent=2))
    
    if token_response.status_code != 200:
        print("Failed to get access token")
        return
    
    access_token = token_response.json().get('access_token')
    
    # Use a date 7 days from now
    future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    # Flight offers search parameters
    params = {
        'originLocationCode': 'DEL',
        'destinationLocationCode': 'BOM',
        'departureDate': future_date,
        'adults': 1,
        'travelClass': 'ECONOMY',
        'includedAirlineCodes': '6E,AI,IX,QP',
        'nonStop': 'false',
        'currencyCode': 'INR',
        'max': 25
    }
    
    # Make flight offers request
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    flight_offers_url = f"{base_url}/v2/shopping/flight-offers"
    response = requests.get(flight_offers_url, headers=headers, params=params)
    
    print("\nFlight Offers Response Status:", response.status_code)
    print("Flight Offers Response:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_amadeus()