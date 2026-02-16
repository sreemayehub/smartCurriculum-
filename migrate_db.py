import sqlite3
import os

DB_NAME = "smart_curriculum.db"

def migrate():
    # Find database in backend folder if running from root
    db_path = DB_NAME
    if not os.path.exists(db_path):
        db_path = os.path.join("backend", DB_NAME)
    
    if not os.path.exists(db_path):
        print(f"Error: {DB_NAME} not found.")
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    columns_to_add = [
        ("profile_pic", "TEXT"),
        ("branch", "TEXT"),
        ("learning_preferences", "TEXT")
    ]
    
    for col_name, col_type in columns_to_add:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            print(f"Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column {col_name} already exists.")
            else:
                print(f"Error adding {col_name}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
