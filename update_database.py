import os
import mysql.connector
from dotenv import load_dotenv

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

def update_users_table():
    """Update the users table with the new schema"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the password column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'users' 
            AND COLUMN_NAME = 'password'
        """, (os.getenv('MYSQL_DB', 'flight_booking'),))
        
        if not cursor.fetchone():
            print("Adding password column to users table...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN password VARCHAR(255) NOT NULL AFTER email,
                ADD COLUMN mobile VARCHAR(15) UNIQUE AFTER name
            """)
            conn.commit()
            print("Successfully updated users table")
        else:
            print("Users table already has the required columns")
            
        # Check if the mobile column has a unique constraint
        cursor.execute("""
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'users' 
            AND CONSTRAINT_TYPE = 'UNIQUE'
            AND CONSTRAINT_NAME = 'mobile'
        """, (os.getenv('MYSQL_DB', 'flight_booking'),))
        
        if not cursor.fetchone():
            print("Adding unique constraint to mobile column...")
            try:
                cursor.execute("""
                    ALTER TABLE users 
                    ADD CONSTRAINT mobile UNIQUE (mobile)
                """)
                conn.commit()
                print("Successfully added unique constraint to mobile column")
            except mysql.connector.Error as err:
                print(f"Error adding unique constraint to mobile column: {err}")
                
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("Updating database schema...")
    update_users_table()
    print("Database update complete")
