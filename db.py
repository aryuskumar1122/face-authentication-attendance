import sqlite3

DB_PATH = "data/attendance.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        reg_no TEXT PRIMARY KEY,
        name TEXT NOT NULL
    )
    """)

    cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_no TEXT,
    name TEXT,
    date TEXT,
    in_time TEXT,
    out_time TEXT
)
""")


    conn.commit()
    conn.close()
