import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_connection():
    try:
        print("Testing MySQL connection...")
        print(f"Host: {os.getenv('MYSQL_HOST')}")
        print(f"User: {os.getenv('MYSQL_USER')}")
        print(f"Database: {os.getenv('MYSQL_DB')}")
        
        # Try to connect without database first
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', '')
        )
        
        print("✅ Successfully connected to MySQL server")
        
        # Check if database exists
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE %s", (os.getenv('MYSQL_DB', 'flight_booking'),))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Database '{os.getenv('MYSQL_DB')}' exists")
        else:
            print(f"❌ Database '{os.getenv('MYSQL_DB')}' does not exist")
            create_db = input("Would you like to create it? (y/n): ")
            if create_db.lower() == 'y':
                cursor.execute(f"CREATE DATABASE {os.getenv('MYSQL_DB', 'flight_booking')}")
                print(f"✅ Created database '{os.getenv('MYSQL_DB')}'")
            
        cursor.close()
        conn.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        print("\nTroubleshooting tips:")
        print("1. Make sure MySQL server is running")
        print("2. Check your MySQL username and password in the .env file")
        print("3. Try connecting with MySQL Workbench or MySQL CLI to verify credentials")

if __name__ == "__main__":
    test_connection()
