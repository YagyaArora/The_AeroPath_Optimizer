from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import airportsdata
from math import radians, sin, cos, sqrt, atan2
import requests
import json
import os
import mysql.connector
from dotenv import load_dotenv
import uuid
import bcrypt
import jwt
from auth_routes import auth_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

def init_db():
    """Initialize the database and create tables if they don't exist"""
    try:
        # First connect without database to create it if needed
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('MYSQL_DB', 'flight_booking')}")
        cursor.close()
        conn.close()
        
        # Now connect to the database and create tables
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                mobile VARCHAR(15) UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                flight_number VARCHAR(20) NOT NULL,
                airline VARCHAR(100) NOT NULL,
                origin VARCHAR(3) NOT NULL,
                destination VARCHAR(3) NOT NULL,
                departure_time DATETIME NOT NULL,
                arrival_time DATETIME NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                currency VARCHAR(3) DEFAULT 'INR',
                cabin_class VARCHAR(20) NOT NULL,
                booking_reference VARCHAR(36) UNIQUE NOT NULL,
                status VARCHAR(20) DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and tables initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

# MySQL connection helper
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'flight_booking')
    )

# Register blueprints
app.register_blueprint(auth_bp)

# Update CORS configuration to allow authorization header and handle preflight requests
CORS(app, resources={
    r"/*": {
        "origins": "http://localhost:3000",
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "supports_credentials": True
    }
})

# Amadeus API Configuration
AMADEUS_API_KEY = "BqDtPNTcgYsPP0X88iGrEsG3IMNzRpoS"
AMADEUS_API_SECRET = "cr0APVNsSEoceqUt"
AMADEUS_BASE_URL = "https://test.api.amadeus.com"

# Token management
token_data = {
    "access_token": None,
    "expires_at": None
}

def get_amadeus_token():
    """Get a new Amadeus API access token or return existing valid token"""
    global token_data
    
    current_time = datetime.now()
    
    # Check if we have a valid token
    if token_data["access_token"] and token_data["expires_at"] and current_time < token_data["expires_at"]:
        return token_data["access_token"]
    
    # Get new token
    try:
        token_url = f"{AMADEUS_BASE_URL}/v1/security/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_API_KEY,
            "client_secret": AMADEUS_API_SECRET
        }
        
        response = requests.post(token_url, headers=headers, data=data)
        response.raise_for_status()
        
        token_response = response.json()
        token_data["access_token"] = token_response["access_token"]
        # Set expiration time (subtract 5 minutes for safety margin)
        token_data["expires_at"] = current_time + timedelta(seconds=token_response["expires_in"] - 300)
        
        return token_data["access_token"]
    except Exception as e:
        print(f"Error getting Amadeus token: {str(e)}")
        return None

# Update the after_request handler to include Authorization in allowed headers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Vary'] = 'Origin'
    return response

# Handle OPTIONS method for preflight requests
@app.route('/api/optimize', methods=['OPTIONS'])
def options_handler():
    response = jsonify({'status': 'success'})
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    return response

# Load airport data
try:
    print("Loading airport data...")
    airports = airportsdata.load('iata')
    print(f"Loaded airports dictionary type: {type(airports)}")
    print(f"Number of airports: {len(airports)}")
    
    # Check if airports is empty
    if not airports:
        print("Warning: Airports dictionary is empty!")
    else:
        # Print first airport details
        first_iata = next(iter(airports))
        first_airport = airports[first_iata]
        print(f"First airport IATA: {first_iata}")
        print(f"First airport details: {first_airport}")
        
        # Check if required fields exist
        required_fields = ['name', 'city', 'country']
        missing_fields = [field for field in required_fields if field not in first_airport]
        if missing_fields:
            print(f"Warning: Missing required fields in airport data: {missing_fields}")
except Exception as e:
    print(f"Error loading airports: {str(e)}")
    airports = {}
    print("Using empty airports dictionary")

# Test airport loading
print("\nTesting airport loading:")
if airports:
    test_iatas = ['DEL', 'BOM', 'MAA']  # Test with some common Indian airports
    for iata in test_iatas:
        airport = airports.get(iata)
        print(f"\nTesting airport {iata}:")
        if airport:
            print(f"Found airport: {airport}")
            print(f"Airport name: {airport.get('name', 'N/A')}")
            print(f"Airport city: {airport.get('city', 'N/A')}")
            print(f"Airport country: {airport.get('country', 'N/A')}")
        else:
            print(f"Airport {iata} not found!")
else:
    print("Airports dictionary is empty!")

# Test a specific airport
try:
    delhi_airport = airports.get('DEL')
    if delhi_airport:
        print(f"Found DEL airport: {delhi_airport}")
    else:
        print("DEL airport not found")
except Exception as e:
    print(f"Error testing airport: {str(e)}")
    print(f"Loaded {len(airports)} airports")

# Function to get airport coordinates
def get_airport_coordinates(iata_code):
    if iata_code in airports:
        airport = airports[iata_code]
        return {
            'lat': float(airport['lat']),
            'lng': float(airport['lon'])
        }
    return None

# Function to search airports by city or name
def search_airports(query):
    try:
        if not query:
            print("Error: Empty query received")
            return []
            
        query = query.lower()
        print(f"\nSearching for airports with query: {query}")
        print(f"Airports dictionary type: {type(airports)}")
        print(f"Number of airports: {len(airports)}")
        
        if not airports:
            print("Error: Airports dictionary is empty!")
            return []
            
        results = []
        
        # Check a few airports to verify data structure
        test_airports = list(airports.items())[:3]
        for iata, airport in test_airports:
            print(f"\nTesting airport {iata}:")
            print(f"Airport data: {airport}")
            print(f"Airport name: {airport.get('name', 'N/A')}")
            print(f"Airport city: {airport.get('city', 'N/A')}")
            print(f"Airport country: {airport.get('country', 'N/A')}")
        
        # Perform search
        for iata, airport in airports.items():
            if not isinstance(airport, dict):
                print(f"Warning: Invalid airport data type for {iata}: {type(airport)}")
                continue
                
            # Check each field
            city_match = query in airport.get('city', '').lower()
            name_match = query in airport.get('name', '').lower()
            iata_match = query in iata.lower()
            country_match = query in airport.get('country', '').lower()
            
            if city_match or name_match or iata_match or country_match:
                result = {
                    'iata': iata,
                    'name': airport['name'],
                    'city': airport.get('city', ''),
                    'state': airport.get('state', ''),
                    'country': airport.get('country', '')
                }
                print(f"Found matching airport: {result}")
                results.append(result)
        
        # Sort by relevance
        results.sort(key=lambda x: 
            (x['iata'].lower().startswith(query),
             x['city'].lower().startswith(query),
             x['name'].lower().startswith(query)),
            reverse=True)
        
        print(f"\nSearch complete - Found {len(results)} matching airports")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['iata']}: {result['name']} ({result['city']}, {result['country']})")
        
        return results[:10]  # Limit to top 10 results
    except Exception as e:
        print(f"Error in search_airports: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []

@app.route('/api/airports', methods=['GET'])
def get_airports():
    try:
        query = request.args.get('q', '').lower()
        print(f"\nReceived airport search request with query: {query}")
        
        if not query:
            print("No query provided")
            return jsonify({
                'airports': [],
                'message': 'Please provide a search query'
            })
        
        print(f"Searching for airports with query: {query}")
        results = search_airports(query)
        print(f"Found {len(results)} airports")
        
        if not results:
            print("No airports found for query")
            return jsonify({
                'airports': [],
                'message': 'No airports found matching your query'
            })
        
        print("Returning airport results:")
        for result in results:
            print(f"- {result['iata']}: {result['name']} ({result['city']}, {result['country']})")
        
        return jsonify({
            'airports': results,
            'message': f'Found {len(results)} airports matching "{query}"'
        })
    except Exception as e:
        print(f"Error fetching airports: {str(e)}")
        return jsonify({
            'error': f'Failed to fetch airports: {str(e)}',
            'message': 'Please try again later'
        }), 500

# Route to optimize route

# --- USER REGISTRATION ENDPOINT ---
@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    user_id = str(uuid.uuid4())
    email = data['email']
    name = data['name']
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, email, name) VALUES (%s, %s, %s)",
            (user_id, email, name)
        )
        conn.commit()
        return jsonify({'user_id': user_id, 'email': email, 'name': name}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()

# --- FLIGHT BOOKING ENDPOINT ---
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    booking_reference = str(uuid.uuid4())
    try:
        cursor.execute("""
            INSERT INTO bookings (
                user_id, flight_number, airline, origin, destination,
                departure_time, arrival_time, price, currency, cabin_class, booking_reference
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['user_id'],
            data['flight_number'],
            data['airline'],
            data['origin'],
            data['destination'],
            data['departure_time'],
            data['arrival_time'],
            data['price'],
            data.get('currency', 'INR'),
            data.get('cabin_class', 'ECONOMY'),
            booking_reference
        ))
        conn.commit()
        return jsonify({'booking_reference': booking_reference}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()

# --- GET BOOKINGS FOR A USER ---
@app.route('/api/users/<user_id>/bookings', methods=['GET'])
def get_user_bookings(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM bookings WHERE user_id = %s", (user_id,))
        bookings = cursor.fetchall()
        return jsonify(bookings)
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/optimize', methods=['POST', 'OPTIONS'])
def optimize_route():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'success'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response
        
    try:
        # Add request body logging
        print("Received request data:", request.get_json())
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No request data provided'}), 400
            
        source = data.get('source')
        destination = data.get('destination')
        date = data.get('date')
        
        print(f"Processing flight search: {source} to {destination} on {date}")
        
        # Validate required fields
        if not all([source, destination, date]):
            missing_fields = []
            if not source: missing_fields.append('source')
            if not destination: missing_fields.append('destination')
            if not date: missing_fields.append('date')
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Get fresh token
        access_token = get_amadeus_token()
        if not access_token:
            return jsonify({'error': 'Failed to authenticate with Amadeus API'}), 500

        # Search flights using Amadeus API
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        search_url = f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers"
        params = {
            "originLocationCode": source.upper(),
            "destinationLocationCode": destination.upper(),
            "departureDate": date,
            "adults": "1",
            "children": "0",
            "infants": "0",
            "travelClass": "ECONOMY",
            "nonStop": "false",
            "currencyCode": "INR",
            "max": "25"
        }
        
        print(f"Making Amadeus API request to {search_url}")
        print("Request params:", params)
        
        response = requests.get(search_url, headers=headers, params=params)
        
        # Log the response for debugging
        print(f"Amadeus API response status: {response.status_code}")
        print("Amadeus API response:", response.text[:500])  # Print first 500 chars of response
        
        if response.status_code == 401:
            # Token might be invalid, clear it and try once more
            token_data["access_token"] = None
            access_token = get_amadeus_token()
            if access_token:
                headers["Authorization"] = f"Bearer {access_token}"
                response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code == 400:
            error_data = response.json()
            error_message = error_data.get('errors', [{}])[0].get('detail', 'Invalid request')
            return jsonify({'error': f'API Error: {error_message}'}), 400
            
        response.raise_for_status()
        flight_data = response.json()

        if not flight_data.get('data'):
            return jsonify({
                'flights': [],
                'message': 'No flights found for the specified route and date'
            })

        # Process and format flight results
        flights = []
        for offer in flight_data.get('data', []):
            try:
                itinerary = offer['itineraries'][0]
                segment = itinerary['segments'][0]
                price = float(offer['price']['total'])
                
                # Get airline name from dictionaries
                airline_code = segment['carrierCode']
                airline_name = flight_data.get('dictionaries', {}).get('carriers', {}).get(airline_code, airline_code)
                
                flight = {
                    'airline': airline_name,
                    'flightNumber': f"{airline_code}{segment['number']}",
                    'origin': segment['departure']['iataCode'],
                    'destination': segment['arrival']['iataCode'],
                    'departureTime': segment['departure']['at'],
                    'arrivalTime': segment['arrival']['at'],
                    'duration': itinerary['duration'],
                    'price': price,
                    'currency': offer['price']['currency'],
                    'numberOfStops': segment.get('numberOfStops', 0),
                    'aircraft': flight_data.get('dictionaries', {}).get('aircraft', {}).get(segment['aircraft']['code'], 'Unknown Aircraft'),
                    'cabin': offer['travelerPricings'][0]['fareDetailsBySegment'][0]['cabin']
                }
                
                # Add baggage info if available
                try:
                    flight['baggage'] = {
                        'checked': offer['travelerPricings'][0]['fareDetailsBySegment'][0].get('includedCheckedBags', {}),
                        'cabin': offer['travelerPricings'][0]['fareDetailsBySegment'][0].get('includedCabinBags', {})
                    }
                except Exception as e:
                    print(f"Warning: Could not get baggage info: {str(e)}")
                    flight['baggage'] = {'checked': {}, 'cabin': {}}
                
                flights.append(flight)
            except Exception as e:
                print(f"Warning: Error processing flight offer: {str(e)}")
                continue

        # Sort flights by price
        flights.sort(key=lambda x: x['price'])
        
        return jsonify({
            'flights': flights,
            'source': source.upper(),
            'destination': destination.upper(),
            'date': date,
            'total_flights': len(flights)
        })

    except requests.exceptions.RequestException as e:
        print(f"Error fetching flight data: {str(e)}")
        return jsonify({
            'error': f'Failed to fetch flight data: {str(e)}'
        }), 500
    except Exception as e:
        import traceback
        print(f"Error processing flight data: {str(e)}")
        print("Traceback:", traceback.format_exc())
        return jsonify({
            'error': f'Failed to process flight data: {str(e)}'
        }), 500

@app.route('/test-airports', methods=['GET'])
def test_airports():
    try:
        # Test with a sample query
        test_query = "DEL"
        print(f"\nTesting airport search with query: {test_query}")
        
        # Get results
        results = search_airports(test_query)
        print(f"\nFound {len(results)} airports:")
        for result in results:
            print(f"- {result['iata']}: {result['name']} ({result['city']}, {result['country']})")
        
        return jsonify({
            'query': test_query,
            'results': results,
            'message': f'Found {len(results)} airports'
        })
    except Exception as e:
        print(f"Error in test endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500



@app.route('/')
def home():
    return "<h1>Flight Route Optimizer API is running!</h1><p>Try accessing <a href='/test-airports'>/test-airports</a> to test the airport search.</p>"

# Add a secret key for JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

if __name__ == '__main__':
    try:
        # Initialize database
        print("Initializing database...")
        init_db()
        print("Database initialized successfully")
        
        # Test database connection
        try:
            conn = get_db_connection()
            if conn.is_connected():
                print("Successfully connected to MySQL database")
                cursor = conn.cursor()
                cursor.execute("SELECT DATABASE();")
                db_name = cursor.fetchone()[0]
                print(f"✅ Using database: {db_name}")
                cursor.close()
                conn.close()
        except Exception as e:
            print("❌ Error connecting to MySQL:", str(e))
            print("\nPlease check your MySQL server and .env configuration:")
            print(f"- Is MySQL running? (Check with: net start | findstr mysql)")
            print(f"- Check if database 'flight_booking' exists")
            print(f"- Verify username/password in .env file")
            exit(1)
            
        # Test airport search
        test_query = "DEL"
        print(f"\nTesting airport search with query: {test_query}")
        try:
            results = search_airports(test_query)
            print("\nSearch Results:")
            for result in results[:3]:  # Show first 3 results to keep output clean
                print(f"- {result['iata']}: {result['name']} ({result['city']}, {result['country']})")
            if len(results) > 3:
                print(f"... and {len(results)-3} more results")
        except Exception as e:
            print(f"⚠️  Error during airport search: {str(e)}")
        
        # Run Flask app
        print("\n🚀 Starting Flask server...")
        print("🌐 Server running at: http://localhost:5000")
        print("🔌 Press CTRL+C to stop the server")
        app.run(debug=True, port=5000, host='0.0.0.0')
        
    except Exception as e:
        print("\n❌ An error occurred:", str(e))
        print("\nTroubleshooting tips:")
        print("1. Make sure MySQL server is running")
        print("2. Verify your .env file has correct MySQL credentials")
        print("3. Check if the 'flight_booking' database exists")
        print("4. Try running 'python -c \"import mysql.connector; print('MySQL Connector is installed')\"' to verify the MySQL connector")
        exit(1)
