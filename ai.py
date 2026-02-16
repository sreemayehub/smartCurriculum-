from flask import Blueprint, request, jsonify
from database import get_db_connection
import json

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message', '').lower()
    
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    curriculum = conn.execute('SELECT * FROM curriculum WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    if not user_data:
        return jsonify({'error': 'User not found'}), 404
        
    user_name = user_data['name']
    career_goal = user_data['career_goal']
    
    # Basic rule-based AI engine for curriculum context
    response = ""
    
    if "hello" in message or "hi " in message or message == "hi":
        response = f"Hello {user_name}! I'm your SmartCurriculum Assistant. How can I help you with your {career_goal} journey today?"
    elif "progress" in message or "how am i doing" in message:
        completed = sum(1 for item in curriculum if item['status'] == 'completed')
        total = len(curriculum)
        if total > 0:
            percentage = (completed / total) * 100
            response = f"You have completed {completed} out of {total} topics ({percentage:.1f}%). You're doing great!"
        else:
            response = "You haven't started your curriculum yet. Go to your profile to generate one!"
    elif "what should i study" in message or "next" in message:
        next_topic = next((item for item in curriculum if item['status'] != 'completed'), None)
        if next_topic:
            response = f"Your next focus should be '{next_topic['topic']}'. It's a {next_topic['difficulty_level']} level topic."
        else:
            response = "Congratulations! You've completed your current curriculum. Time to set a new goal?"
    elif "curriculum" in message or "course" in message:
        response = f"Your current curriculum is tailored for a {career_goal} role. It consists of {len(curriculum)} key topics spanning multiple weeks."
    elif "help" in message:
        response = "I can help you understand your progress, tell you what to study next, or explain your curriculum goals. Just ask!"
    else:
        response = f"That's an interesting question! As your SmartCurriculum assistant, I'm here to guide you through your {career_goal} path. Could you tell me more about what specifically you'd like to know regarding your topics or progress?"

    return jsonify({
        'response': response,
        'sender': 'bot'
    }), 200
