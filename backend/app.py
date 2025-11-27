from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# Database Configuration (Cloud SQL or local MySQL)
db_config = {
    'host': '10.161.32.3',  # Use localhost if using Cloud SQL Proxy, or the private IP for Cloud SQL
    'user': 'root',  # Replace with your MySQL user
    'password': 'Tejuaws@123',  # Replace with your MySQL password
    'database': 'dev',  # Replace with your database name
    'port': 3306  # Default MySQL port
}

# Connect to MySQL
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        app.logger.error(f"Error connecting to database: {err}")
        return None

# 1️⃣ Get all users
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")  # Replace 'users' with your table name
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users)

# 2️⃣ Get user by ID
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    if user:
        return jsonify(user)
    return jsonify({'error': 'User not found'}), 404

# 3️⃣ Add a new user
@app.route('/users/add', methods=['POST'])
def add_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')

    # Validate input
    if not name or not email:
        return jsonify({'error': 'Name and Email are required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email)
        )
        conn.commit()
        return jsonify({'message': 'User added successfully'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# 4️⃣ Update user by ID
@app.route('/users/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    name = data.get('name')
    email = data.get('email')

    if not name or not email:
        return jsonify({'error': 'Name and Email are required'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    try:
        cursor.execute(
            "UPDATE users SET name = %s, email = %s WHERE id = %s",
            (name, email, user_id)
        )
        conn.commit()
        return jsonify({'message': 'User updated successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# 5️⃣ Delete user by ID
@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'User not found'}), 404

    try:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({'message': 'User deleted successfully'})
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# 🔹 Simple Hello route
@app.route('/')
def index():
    return "Hello from the Flask Backend!"

# Entry Point
if __name__ == '__main__':
    # Run the Flask application
    app.run(host='0.0.0.0', port=8080, debug=True)
