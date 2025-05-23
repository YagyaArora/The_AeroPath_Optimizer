import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'flight_booking')
    )

def update_users_table():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Add password and mobile columns if they don't exist
        cursor.execute("""
            AL TABLE users
            ADD COLUMN IF NOT EXISTS password VARCHAR(255) NOT NULL AFTER email,
            ADD COLUMN IF NOT EXISTS mobile VARCHAR(15) UNIQUE AFTER name
        """)
        
        conn.commit()
        print("Successfully updated users table")
        
    except Exception as e:
        print(f"Error updating users table: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    update_users_table()
