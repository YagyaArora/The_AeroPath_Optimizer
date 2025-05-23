import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

try:
    print("Testing MySQL connection...")
    
    # Try to connect to MySQL server
    conn = mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', '')
    )
    
    print("✅ Successfully connected to MySQL server")
    
    # Create a cursor
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SHOW DATABASES")
    print("\nAvailable databases:")
    for db in cursor:
        print(f"- {db[0]}")
    
    # Close the connection
    cursor.close()
    conn.close()
    
except mysql.connector.Error as err:
    print(f"❌ Error: {err}")
    print("\nTroubleshooting:")
    print("1. Make sure MySQL server is running")
    print("2. Check your .env file for correct MySQL credentials")
    print("3. Try connecting with: mysql -u root -p")
    print("4. If you forgot password, you may need to reset MySQL root password")
