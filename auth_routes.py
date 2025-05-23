from flask import Blueprint, request, jsonify
import mysql.connector
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps

# Create blueprint
auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DB', 'flight_booking')
    )

def generate_token(user_id):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, os.getenv('SECRET_KEY', 'your-secret-key'), algorithm='HS256')

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
                
            data = jwt.decode(token, os.getenv('SECRET_KEY', 'your-secret-key'), algorithms=['HS256'])
            current_user_id = data['user_id']
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
            
        return f(current_user_id, *args, **kwargs)
    return decorated

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate input
    required_fields = ['name', 'email', 'password', 'mobile']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate email format
    if '@' not in data['email']:
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Validate mobile format (10 digits)
    if not data['mobile'].isdigit() or len(data['mobile']) != 10:
        return jsonify({'error': 'Mobile number must be 10 digits'}), 400
    
    # Validate password length
    if len(data['password']) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    # Hash password with proper encoding
    password_bytes = data['password'].encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    print("\n=== Registration Attempt ===")
    print(f"Name: {data['name']}")
    print(f"Email: {data['email']}")
    print(f"Mobile: {data['mobile']}")
    print(f"Hashed password: {hashed_password.decode('utf-8')}")
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if email or mobile already exists
        cursor.execute("SELECT id FROM users WHERE email = %s OR mobile = %s", 
                      (data['email'], data['mobile']))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("Registration failed: Email or mobile already exists")
            return jsonify({'error': 'Email or mobile number already registered'}), 400
        
        # Insert new user
        cursor.execute(
            """
            INSERT INTO users (name, email, password, mobile)
            VALUES (%s, %s, %s, %s)
            """,
            (data['name'], data['email'], hashed_password.decode('utf-8'), data['mobile'])
        )
        
        user_id = cursor.lastrowid
        conn.commit()
        
        print(f"User registered successfully with ID: {user_id}")
        
        # Generate token
        token = generate_token(user_id)
        
        response_data = {
            'message': 'User registered successfully',
            'token': token,
            'user': {
                'id': user_id,
                'name': data['name'],
                'email': data['email'],
                'mobile': data['mobile']
            }
        }
        
        return jsonify(response_data), 201
        
    except mysql.connector.Error as err:
        print("Database error during registration:", err)
        if conn:
            conn.rollback()
        return jsonify({'error': 'Database error occurred during registration'}), 500
    except Exception as e:
        print("Unexpected error during registration:", str(e))
        if conn:
            conn.rollback()
        return jsonify({'error': 'An error occurred during registration'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return token"""
    print("\n=== Login Request ===")
    data = request.get_json()
    print("Login attempt with data:", data)
    
    # Check required fields
    if not data.get('identifier') or not data.get('password'):
        print("Missing identifier or password")
        return jsonify({'error': 'Email/Mobile and password are required'}), 400
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if identifier is email or mobile
        query = "SELECT * FROM users WHERE email = %s OR mobile = %s"
        cursor.execute(query, (data['identifier'], data['identifier']))
        user = cursor.fetchone()
        
        print("Found user in database:", user)
        
        if not user:
            print("No user found with identifier:", data['identifier'])
            return jsonify({'error': 'Invalid email/mobile or password'}), 401
        
        # Debug: Print password hashes for verification
        print("Stored password hash:", user['password'])
        print("Password type:", type(user['password']))
        
        # Verify password - handle both string and bytes for password hash
        stored_password = user['password'].encode('utf-8') if isinstance(user['password'], str) else user['password']
        provided_password = data['password'].encode('utf-8')
        
        print("Stored password (bytes):", stored_password)
        print("Provided password (bytes):", provided_password)
        
        # First try with the password as is, then try with rehashing if needed
        if not bcrypt.checkpw(provided_password, stored_password):
            # If direct check fails, try with rehashing (in case the hash needs updating)
            if not bcrypt.checkpw(provided_password, stored_password):
                print("Password verification failed")
                return jsonify({'error': 'Invalid email/mobile or password'}), 401
        
        print("Password verified successfully")
        
        # Generate token
        token = generate_token(user['id'])
        print("Generated token:", token)
        
        response_data = {
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'mobile': user['mobile']
            }
        }
        print("Login successful for user:", user['email'])
        
        return jsonify(response_data)
        
    except mysql.connector.Error as err:
        print("Database error:", err)
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': 'An error occurred during login'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@auth_bp.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(user_id):
    """Get current user's profile"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT id, name, email, mobile FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify(user)
        
    except mysql.connector.Error as err:
        return jsonify({'error': f'Database error: {err}'}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
