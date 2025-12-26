import sqlite3
from contextlib import contextmanager

DB_PATH = "survey.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            user_id INTEGER PRIMARY KEY,
            age_group TEXT,
            city TEXT,
            exam_name TEXT,
            exam_type TEXT,
            test_subtype TEXT,
            task_count INTEGER,
            time_minutes INTEGER,
            attempts TEXT,
            passing_score TEXT,
            required_result TEXT,
            exam_date TEXT,
            importance TEXT,
            has_examples TEXT, 
            exam_location TEXT,
            device_type TEXT,
            has_camera TEXT,
            proctoring_type TEXT,
            proctoring_system TEXT,
            other_proctoring TEXT,
            camera_count INTEGER, 
            materials_exist TEXT,
            materials_format TEXT,
            paper_type TEXT,
            textbook_pages INTEGER,
            digital_types TEXT, 
            assistant_welcome TEXT,
            assistant_time TEXT, 
            payment_agreement TEXT,
            assistant_price INTEGER,
            exam_support_price INTEGER,
            materials_prep_price INTEGER
        )
    """)
    conn.commit()
    conn.close()

@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def save_response(user_id: int, **kwargs):
    if not kwargs:
        return

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM responses WHERE user_id = ?", (user_id,))
        exists = cursor.fetchone() is not None

        if exists:
            set_clause = ", ".join([f"{key} = ?" for key in kwargs])
            values = list(kwargs.values()) + [user_id]
            query = f"UPDATE responses SET {set_clause} WHERE user_id = ?"
            cursor.execute(query, values)
        else:
            keys = ["user_id"] + list(kwargs.keys())
            placeholders = ["?"] * len(keys)
            values = [user_id] + list(kwargs.values())
            query = f"INSERT INTO responses ({', '.join(keys)}) VALUES ({', '.join(placeholders)})"
            cursor.execute(query, values)
        conn.commit()