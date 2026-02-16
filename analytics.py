from flask import Blueprint, jsonify, request
from database import get_db_connection

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_curriculum_items = conn.execute('SELECT COUNT(*) FROM curriculum').fetchone()[0]
    completed_items = conn.execute("SELECT COUNT(*) FROM curriculum WHERE status = 'completed'").fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "total_users": total_users,
        "total_curriculum_items": total_curriculum_items,
        "completed_items": completed_items,
        "top_skills": ["Python", "React", "Data Science", "Machine Learning"] # Mock data for demo
    }), 200

@analytics_bp.route('/user-stats', methods=['POST'])
def get_user_stats():
    """Get analytics for a specific user"""
    data = request.json
    user_id = data.get('user_id')
    
    conn = get_db_connection()
    
    # Get user's curriculum data
    curriculum = conn.execute('SELECT * FROM curriculum WHERE user_id = ?', (user_id,)).fetchall()
    
    total_topics = len(curriculum)
    completed_topics = len([c for c in curriculum if c['status'] == 'completed'])
    pending_topics = total_topics - completed_topics
    progress_percentage = (completed_topics / total_topics * 100) if total_topics > 0 else 0
    
    # Breakdown by difficulty
    difficulty_breakdown = {}
    for item in curriculum:
        level = item['difficulty_level']
        if level not in difficulty_breakdown:
            difficulty_breakdown[level] = {'total': 0, 'completed': 0}
        difficulty_breakdown[level]['total'] += 1
        if item['status'] == 'completed':
            difficulty_breakdown[level]['completed'] += 1
    
    conn.close()
    
    return jsonify({
        "total_topics": total_topics,
        "completed_topics": completed_topics,
        "pending_topics": pending_topics,
        "progress_percentage": progress_percentage,
        "difficulty_breakdown": difficulty_breakdown
    }), 200

