import os
import mysql.connector
from dotenv import load_dotenv
import bcrypt

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

def init_database():
    """Initialize the database with sample data"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Drop tables if they exist (in the correct order to respect foreign key constraints)
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DROP TABLE IF EXISTS bookings")
        cursor.execute("DROP TABLE IF EXISTS flights")
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("DROP TABLE IF EXISTS airports")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            mobile VARCHAR(15) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS airports (
            id INT NOT NULL AUTO_INCREMENT,
            code VARCHAR(10) NOT NULL,
            name VARCHAR(100) NOT NULL,
            city VARCHAR(100) NOT NULL,
            country VARCHAR(100) NOT NULL,
            latitude DECIMAL(10, 8) NOT NULL,
            longitude DECIMAL(11, 8) NOT NULL,
            timezone VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY (code)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INT NOT NULL AUTO_INCREMENT,
            flight_number VARCHAR(20) NOT NULL,
            airline VARCHAR(100) NOT NULL,
            source_airport_id INT NOT NULL,
            destination_airport_id INT NOT NULL,
            departure_time DATETIME NOT NULL,
            arrival_time DATETIME NOT NULL,
            price DECIMAL(10, 2) NOT NULL,
            available_seats INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            FOREIGN KEY (source_airport_id) REFERENCES airports(id) ON DELETE CASCADE,
            FOREIGN KEY (destination_airport_id) REFERENCES airports(id) ON DELETE CASCADE,
            INDEX (departure_time),
            INDEX (arrival_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT NOT NULL AUTO_INCREMENT,
            user_id INT NOT NULL,
            flight_id INT NOT NULL,
            booking_reference VARCHAR(20) NOT NULL,
            passenger_name VARCHAR(100) NOT NULL,
            passenger_email VARCHAR(100) NOT NULL,
            passenger_phone VARCHAR(20) NOT NULL,
            seat_number VARCHAR(10) NOT NULL,
            booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('confirmed', 'cancelled', 'completed') DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id),
            UNIQUE KEY (booking_reference),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE,
            INDEX (booking_date),
            INDEX (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Insert sample airports if they don't exist
        cursor.execute("SELECT COUNT(*) FROM airports")
        if cursor.fetchone()[0] == 0:
            airports = [
                ('JFK', 'John F. Kennedy International Airport', 'New York', 'USA', 40.6413, -73.7781, 'America/New_York'),
                ('LAX', 'Los Angeles International Airport', 'Los Angeles', 'USA', 33.9416, -118.4085, 'America/Los_Angeles'),
                ('ORD', 'O\'Hare International Airport', 'Chicago', 'USA', 41.9742, -87.9073, 'America/Chicago'),
                ('DFW', 'Dallas/Fort Worth International Airport', 'Dallas', 'USA', 32.8998, -97.0403, 'America/Chicago'),
                ('DEN', 'Denver International Airport', 'Denver', 'USA', 39.8561, -104.6737, 'America/Denver'),
                ('SFO', 'San Francisco International Airport', 'San Francisco', 'USA', 37.6213, -122.3790, 'America/Los_Angeles'),
                ('SEA', 'Seattle-Tacoma International Airport', 'Seattle', 'USA', 47.4502, -122.3088, 'America/Los_Angeles'),
                ('MIA', 'Miami International Airport', 'Miami', 'USA', 25.7932, -80.2906, 'America/New_York'),
                ('ATL', 'Hartsfield-Jackson Atlanta International Airport', 'Atlanta', 'USA', 33.6407, -84.4277, 'America/New_York'),
                ('LAS', 'McCarran International Airport', 'Las Vegas', 'USA', 36.0840, -115.1537, 'America/Los_Angeles')
            ]
            
            insert_airport = """
            INSERT INTO airports (code, name, city, country, latitude, longitude, timezone)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.executemany(insert_airport, airports)
            print(f"Inserted {len(airports)} airports")
        
        # Insert a sample admin user if they don't exist
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = 'admin@example.com'")
        if cursor.fetchone()[0] == 0:
            hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
            insert_user = """
            INSERT INTO users (name, email, password, mobile)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_user, (
                'Admin User',
                'admin@example.com',
                hashed_password.decode('utf-8'),
                '1234567890'
            ))
            print("Created admin user")
        
        conn.commit()
        print("Database initialized successfully!")
        
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialization complete")
