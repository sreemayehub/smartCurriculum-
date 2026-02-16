import sqlite3
import os

DB_NAME = "smart_curriculum.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # User Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            career_goal TEXT,
            skills TEXT,
            weak_subjects TEXT,
            weeks_available INTEGER DEFAULT 8,
            hours_per_day REAL DEFAULT 2.0,
            profile_pic TEXT,
            branch TEXT,
            learning_preferences TEXT -- JSON string
        )
    ''')

    # Curriculum Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            difficulty_level TEXT DEFAULT 'Medium',
            estimated_hours REAL DEFAULT 0,
            week_number INTEGER DEFAULT 1,
            subtopics TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()

