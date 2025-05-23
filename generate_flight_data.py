import random
import mysql.connector
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create a database connection"""
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'flight_booking')
    )

def generate_flight_number():
    """Generate a random flight number"""
    airlines = ['AA', 'UA', 'DL', 'WN', 'B6', 'AS', 'NK', 'F9', 'G4', 'SY']
    return f"{random.choice(airlines)}{random.randint(100, 9999)}"

def generate_flight_duration():
    """Generate a random flight duration between 1 and 8 hours"""
    return random.randint(60, 480)  # in minutes

def generate_flight_price(base_price=100):
    """Generate a random flight price"""
    return round(base_price * random.uniform(0.8, 2.5), 2)

def generate_sample_flights(num_flights=100):
    """Generate sample flight data"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all airport IDs
        cursor.execute("SELECT id, code FROM airports")
        airports = cursor.fetchall()
        
        if not airports:
            print("No airports found in the database. Please run init_db.py first.")
            return
        
        # Generate flights
        flights = []
        airlines = [
            'American Airlines', 'United Airlines', 'Delta Air Lines',
            'Southwest Airlines', 'JetBlue Airways', 'Alaska Airlines',
            'Spirit Airlines', 'Frontier Airlines', 'Allegiant Air', 'Sun Country Airlines'
        ]
        
        # Clear existing flights
        cursor.execute("TRUNCATE TABLE flights")
        
        for _ in range(num_flights):
            # Select random source and destination airports (must be different)
            source, destination = random.sample(airports, 2)
            
            # Generate random departure time in the next 30 days
            departure_time = datetime.now() + timedelta(days=random.randint(1, 30), 
                                                      hours=random.randint(0, 23),
                                                      minutes=random.choice([0, 15, 30, 45]))
            
            # Generate random flight duration
            duration = generate_flight_duration()
            arrival_time = departure_time + timedelta(minutes=duration)
            
            # Generate flight data
            flight = {
                'flight_number': generate_flight_number(),
                'airline': random.choice(airlines),
                'source_airport_id': source['id'],
                'destination_airport_id': destination['id'],
                'departure_time': departure_time.strftime('%Y-%m-%d %H:%M:%S'),
                'arrival_time': arrival_time.strftime('%Y-%m-%d %H:%M:%S'),
                'price': generate_flight_price(100 + (duration / 10)),  # Longer flights cost more
                'available_seats': random.randint(5, 300)
            }
            
            # Insert flight
            cursor.execute("""
                INSERT INTO flights (
                    flight_number, airline, source_airport_id, destination_airport_id,
                    departure_time, arrival_time, price, available_seats
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                flight['flight_number'],
                flight['airline'],
                flight['source_airport_id'],
                flight['destination_airport_id'],
                flight['departure_time'],
                flight['arrival_time'],
                flight['price'],
                flight['available_seats']
            ))
            
            flights.append(flight)
        
        conn.commit()
        print(f"Generated {len(flights)} sample flights")
        
    except mysql.connector.Error as err:
        print(f"Error generating sample flights: {err}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("Generating sample flight data...")
    generate_sample_flights(200)  # Generate 200 sample flights
    print("Sample flight data generation complete")
