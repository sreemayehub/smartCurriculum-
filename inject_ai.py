import sqlite3
import json

def inject_curriculum():
    conn = sqlite3.connect('backend/smart_curriculum.db')
    conn.row_factory = sqlite3.Row
    
    # Get the latest user
    user = conn.execute('SELECT id, career_goal FROM users ORDER BY id DESC LIMIT 1').fetchone()
    if not user:
        print("No user found.")
        return
    
    user_id = user['id']
    
    # Clear existing
    conn.execute('DELETE FROM curriculum WHERE user_id = ?', (user_id,))
    
    # Professional 6-week Software Developer Roadmap
    roadmap = [
        {
            "topic": "Frontend Fundamentals & Modern UI",
            "difficulty_level": "Easy",
            "estimated_hours": 20,
            "week_number": 1,
            "subtopics": [
                {"title": "HTML5 Semantic Structure", "completed": False},
                {"title": "CSS3 Flexbox & Grid Layouts", "completed": False},
                {"title": "Responsive Design Principles", "completed": False},
                {"title": "Introduction to React.js Components", "completed": False}
            ]
        },
        {
            "topic": "JavaScript Mastery & Logic",
            "difficulty_level": "Medium",
            "estimated_hours": 24,
            "week_number": 2,
            "subtopics": [
                {"title": "ES6+ Syntax (Arrow functions, Destructuring)", "completed": False},
                {"title": "Asynchronous JS (Promises & Async/Await)", "completed": False},
                {"title": "DOM Manipulation & Event Handling", "completed": False},
                {"title": "State Management Basics", "completed": False}
            ]
        },
        {
            "topic": "Backend Development & APIs",
            "difficulty_level": "Medium",
            "estimated_hours": 28,
            "week_number": 3,
            "subtopics": [
                {"title": "Node.js & Express Server Setup", "completed": False},
                {"title": "RESTful API Design Patterns", "completed": False},
                {"title": "Middleware & Error Handling", "completed": False},
                {"title": "Postman for API Testing", "completed": False}
            ]
        },
        {
            "topic": "Database Systems & Data Modeling",
            "difficulty_level": "Hard",
            "estimated_hours": 25,
            "week_number": 4,
            "subtopics": [
                {"title": "SQL Basics & Relational Databases", "completed": False},
                {"title": "MongoDB & NoSQL Concepts", "completed": False},
                {"title": "ORM/ODM (Sequelize or Mongoose)", "completed": False},
                {"title": "Database Normalization", "completed": False}
            ]
        },
        {
            "topic": "DevOps, Git & Deployment",
            "difficulty_level": "Medium",
            "estimated_hours": 20,
            "week_number": 5,
            "subtopics": [
                {"title": "Advanced Git (Rebase, Cherry-pick)", "completed": False},
                {"title": "Docker Containers & Microservices", "completed": False},
                {"title": "CI/CD Pipelines (GitHub Actions)", "completed": False},
                {"title": "Cloud Deployment (AWS/Vercel/Heroku)", "completed": False}
            ]
        },
        {
            "topic": "Capstone Project & System Design",
            "difficulty_level": "Hard",
            "estimated_hours": 30,
            "week_number": 6,
            "subtopics": [
                {"title": "Full-stack Project Integration", "completed": False},
                {"title": "Scalability & Performance Optimization", "completed": False},
                {"title": "Security Best Practices (JWT, OAuth)", "completed": False},
                {"title": "Technical Interview Preparation", "completed": False}
            ]
        }
    ]
    
    for item in roadmap:
        conn.execute('''
            INSERT INTO curriculum (user_id, topic, status, difficulty_level, estimated_hours, week_number, subtopics)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, item['topic'], 'pending', item['difficulty_level'], item['estimated_hours'], item['week_number'], json.dumps(item['subtopics'])))
    
    conn.commit()
    conn.close()
    print(f"Successfully activated AI curriculum for user {user_id}")

if __name__ == "__main__":
    inject_curriculum()
