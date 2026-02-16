from flask import Blueprint, request, jsonify, send_file
from database import get_db_connection
import io
from fpdf import FPDF
import random
from ai_service import GenerativeAIService

curriculum_bp = Blueprint('curriculum', __name__)

import json

def generate_personalized_curriculum(user_data):
    """Generate a personalized curriculum using AI"""
    career_goal = user_data.get('career_goal', 'Software Engineer')
    weak_subjects = user_data.get('weak_subjects', '')
    weeks = user_data.get('weeks_available', 8)
    hours = user_data.get('hours_per_day', 2.0)
    
    # Call the Generative AI Service
    ai_curriculum = GenerativeAIService.generate_curriculum(career_goal, weak_subjects, weeks, hours)
    
    # Transfer generated list to the expected internal format
    processed_topics = []
    for item in ai_curriculum:
        topic = item.get('topic', 'Topic')
        difficulty = item.get('difficulty_level', 'Medium')
        hours = item.get('estimated_hours', 8)
        week = item.get('week_number', 1)
        subtopics = item.get('subtopics', [])
        
        # Convert subtopics to objects with completion status if they are just strings
        subtopic_objects = []
        for st in subtopics:
            if isinstance(st, str):
                subtopic_objects.append({'title': st, 'completed': False})
            else:
                subtopic_objects.append(st)
                
        processed_topics.append((topic, difficulty, hours, week, subtopic_objects))
    
    return processed_topics

@curriculum_bp.route('/generate', methods=['POST'])
def generate_curriculum():
    data = request.json
    user_id = data.get('user_id')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if curriculum already exists
    existing = conn.execute('SELECT * FROM curriculum WHERE user_id = ?', (user_id,)).fetchall()
    
    if not existing:
        # Get user data for personalization
        user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if user_data:
            user_dict = dict(user_data)
            topics_list = generate_personalized_curriculum(user_dict)
            
            # Insert generated curriculum
            for topic, difficulty, estimated_hours, week_number, subtopics in topics_list:
                subtopics_json = json.dumps(subtopics)
                c.execute('''INSERT INTO curriculum (user_id, topic, status, difficulty_level, estimated_hours, week_number, subtopics) 
                             VALUES (?, ?, ?, ?, ?, ?, ?)''',
                          (user_id, topic, 'pending', difficulty, estimated_hours, week_number, subtopics_json))
            conn.commit()
    
    curriculum = conn.execute('SELECT * FROM curriculum WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    result = []
    for row in curriculum:
        item = dict(row)
        if item.get('subtopics'):
            try:
                # If existing data is list of strings, convert to objects (migration on read/lazy migration)
                # But best to rely on regenerate for full structure. 
                # Here we blindly load. If checks fail frontend might break, so we assume regenerate.
                item['subtopics'] = json.loads(item['subtopics'])
            except:
                item['subtopics'] = []
        result.append(item)
        
    return jsonify(result), 200

@curriculum_bp.route('/regenerate', methods=['POST'])
def regenerate_curriculum():
    """Delete existing curriculum and generate a new one"""
    data = request.json
    user_id = data.get('user_id')
    print(f"Regenerate request for user_id: {user_id}")
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Delete existing curriculum
    c.execute('DELETE FROM curriculum WHERE user_id = ?', (user_id,))
    conn.commit()
    print("Deleted existing curriculum")
    
    # Get user data for personalization
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    if user_data:
        user_dict = dict(user_data)
        print(f"User data found: {user_dict['name']}, goal: {user_dict['career_goal']}")
        topics_list = generate_personalized_curriculum(user_dict)
        print(f"Generated {len(topics_list)} topics")
        
        # Insert new curriculum
        for topic, difficulty, estimated_hours, week_number, subtopics in topics_list:
            subtopics_json = json.dumps(subtopics)
            c.execute('''INSERT INTO curriculum (user_id, topic, status, difficulty_level, estimated_hours, week_number, subtopics) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, topic, 'pending', difficulty, estimated_hours, week_number, subtopics_json))
        conn.commit()
        print("Inserted new curriculum into database")
    else:
        print(f"User not found for ID: {user_id}")
    
    curriculum = conn.execute('SELECT * FROM curriculum WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    result = []
    for row in curriculum:
        item = dict(row)
        if item.get('subtopics'):
            try:
                item['subtopics'] = json.loads(item['subtopics'])
            except:
                item['subtopics'] = []
        result.append(item)
    return jsonify(result), 200

@curriculum_bp.route('/update-status', methods=['POST'])
def update_status():
    """Update the status of a curriculum item"""
    data = request.json
    curriculum_id = data.get('curriculum_id')
    status = data.get('status')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('UPDATE curriculum SET status = ? WHERE id = ?', (status, curriculum_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Status updated successfully'}), 200

@curriculum_bp.route('/update-subtopic', methods=['POST'])
def update_subtopic_status():
    """Update the completion status of a specific subtopic"""
    data = request.json
    curriculum_id = data.get('curriculum_id')
    subtopic_index = data.get('subtopic_index')
    completed = data.get('completed')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get current subtopics
    row = c.execute('SELECT subtopics, status FROM curriculum WHERE id = ?', (curriculum_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Item not found'}), 404
        
    try:
        subtopics = json.loads(row['subtopics'])
        
        # Update the specific subtopic
        if 0 <= subtopic_index < len(subtopics):
            # Check if stored as string (legacy) or dict (new)
            if isinstance(subtopics[subtopic_index], str):
                # Convert to dict if legacy
                subtopics[subtopic_index] = {'title': subtopics[subtopic_index], 'completed': completed}
            else:
                subtopics[subtopic_index]['completed'] = completed
                
            # Check if ALL subtopics are completed
            all_done = all(
                st.get('completed', False) if isinstance(st, dict) else False 
                for st in subtopics
            )
            
            # Optionally auto-complete the parent topic
            new_parent_status = row['status']
            if all_done and row['status'] != 'completed':
                new_parent_status = 'completed'
                c.execute('UPDATE curriculum SET status = ? WHERE id = ?', ('completed', curriculum_id))
            
            # Save updated subtopics
            c.execute('UPDATE curriculum SET subtopics = ? WHERE id = ?', (json.dumps(subtopics), curriculum_id))
            conn.commit()
            
            conn.close()
            return jsonify({
                'message': 'Subtopic updated', 
                'parent_completed': new_parent_status == 'completed',
                'subtopics': subtopics
            }), 200
        else:
            conn.close()
            return jsonify({'error': 'Invalid subtopic index'}), 400
            
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@curriculum_bp.route('/download', methods=['POST'])
def download_curriculum():
    data = request.json
    items = data.get('curriculum', [])
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="SmartCurriculum - Personalized Learning Plan", ln=1, align='C')
    pdf.ln(10)
    
    for idx, item in enumerate(items, 1):
        status_text = f"[{item['status']}]"
        line = f"{idx}. {item['topic']} - {item['difficulty_level']} {status_text}"
        pdf.cell(200, 10, txt=line, ln=1, align='L')
        
        # Add subtopics to PDF
        if item.get('subtopics'):
            pdf.set_font("Arial", size=10)
            for st in item['subtopics']:
                # Handle both string and dict formats for backward compatibility/robustness
                title = st['title'] if isinstance(st, dict) else st
                checked = "[x]" if (isinstance(st, dict) and st.get('completed')) else "[ ]"
                pdf.cell(200, 6, txt=f"   {checked} {title}", ln=1, align='L')
            pdf.set_font("Arial", size=12)
        
    pdf_output = io.BytesIO()
    pdf_string = pdf.output(dest='S').encode('latin-1')
    pdf_output.write(pdf_string)
    pdf_output.seek(0)
    
    return send_file(pdf_output, as_attachment=True, download_name="curriculum.pdf", mimetype='application/pdf')

