import mysql.connector
from dotenv import load_dotenv
import os
from tabulate import tabulate

# Load environment variables
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'flight_booking')
    )

def print_table(conn, table_name):
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    
    if not rows:
        print(f"\nNo data in {table_name}")
        return
        
    print(f"\n=== {table_name.upper()} ===")
    print(tabulate(rows, headers='keys', tablefmt='grid'))
    cursor.close()

def main():
    try:
        conn = get_db_connection()
        
        # Print data from each table
        tables = ['users', 'airports', 'flights', 'bookings']
        for table in tables:
            print_table(conn, table)
            
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    # Install required package if not already installed
    try:
        from tabulate import tabulate
    except ImportError:
        import sys
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate"])
        from tabulate import tabulate
    
    main()
