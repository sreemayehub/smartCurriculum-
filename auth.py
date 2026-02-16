import os
from flask import Blueprint, request, jsonify, send_from_directory
from database import get_db_connection
from werkzeug.utils import secure_filename
import json

auth_bp = Blueprint('auth', __name__)

UPLOAD_FOLDER = 'uploads/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    print(f"Registration request received: {data}")  # Debug logging
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    career_goal = data.get('careerGoal', '')
    weak_subjects = data.get('weakSubjects', '')
    weeks_available = data.get('weeksAvailable', 8)
    hours_per_day = data.get('hoursPerDay', 2.0)
    branch = data.get('branch', '')

    errors = {}

    if not name:
        errors['name'] = "Name is required"
    
    if not email:
        errors['email'] = "Email is required"
    elif '@' not in email or '.' not in email:
        errors['email'] = "Invalid email format"

    if not password:
        errors['password'] = "Password is required"
    elif len(password) < 6:
        errors['password'] = "Password must be at least 6 characters"

    # Validate and convert time parameters
    try:
        weeks_available = int(weeks_available)
        if weeks_available < 1 or weeks_available > 52:
            errors['weeksAvailable'] = "Weeks must be between 1 and 52"
    except (ValueError, TypeError):
        errors['weeksAvailable'] = "Invalid weeks value"
        weeks_available = 8  # fallback

    try:
        hours_per_day = float(hours_per_day)
        if hours_per_day < 0.5 or hours_per_day > 12:
            errors['hoursPerDay'] = "Hours per day must be between 0.5 and 12"
    except (ValueError, TypeError):
        errors['hoursPerDay'] = "Invalid hours per day value"
        hours_per_day = 2.0  # fallback

    if errors:
        print(f"Validation errors: {errors}")  # Debug logging
        return jsonify({"error": "Validation failed", "details": errors}), 400

    conn = get_db_connection()
    c = conn.cursor()
    
    # Check for existing user
    existing_user = c.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({"error": "Registration failed", "details": {"email": "Email already registered"}}), 400

    try:
        c.execute("""INSERT INTO users (name, email, password, career_goal, weak_subjects, weeks_available, hours_per_day, branch) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (name, email, password, career_goal, weak_subjects, weeks_available, hours_per_day, branch))
        conn.commit()
        print(f"User registered successfully: {email}")  # Debug logging
    except Exception as e:
        conn.close()
        print(f"Database error: {e}")
        return jsonify({"error": "Database error", "details": {"general": "An unexpected error occurred"}}), 500
    
    conn.close()
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password)).fetchone()
    conn.close()

    if user:
        # Convert sqlite3.Row to dict to use .get() safely
        user_dict = dict(user)
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user_dict['id'],
                "name": user_dict['name'],
                "email": user_dict['email'],
                "career_goal": user_dict['career_goal'],
                "skills": user_dict.get('skills', ''),
                "weak_subjects": user_dict['weak_subjects'],
                "weeks_available": user_dict.get('weeks_available', 8),
                "hours_per_day": user_dict.get('hours_per_day', 2.0),
                "profile_pic": user_dict.get('profile_pic'),
                "branch": user_dict.get('branch', ''),
                "learning_preferences": json.loads(user_dict.get('learning_preferences', '[]')) if user_dict.get('learning_preferences') else []
            }
        }), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/update-profile', methods=['POST'])
def update_profile():
    """Update user profile information"""
    data = request.json
    user_id = data.get('user_id')
    career_goal = data.get('career_goal')
    skills = data.get('skills')
    weak_subjects = data.get('weak_subjects')
    branch = data.get('branch')
    learning_preferences = json.dumps(data.get('learning_preferences', []))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('''UPDATE users 
                     SET career_goal = ?, skills = ?, weak_subjects = ?, branch = ?, learning_preferences = ? 
                     WHERE id = ?''',
                  (career_goal, skills, weak_subjects, branch, learning_preferences, user_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Profile updated successfully"}), 200
    except Exception as e:
        conn.close()
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to update profile"}), 500

@auth_bp.route('/upload-profile-pic', methods=['POST'])
def upload_profile_pic():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(f"user_{user_id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Update database
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (file_path, user_id))
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Profile picture uploaded", "path": file_path}), 200
    
    return jsonify({"error": "File type not allowed"}), 400

@auth_bp.route('/profile-pics/<path:filename>')
def serve_profile_pic(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


