import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    warnings INTEGER DEFAULT 0
)
""")
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def add_warning(user_id):
    cursor.execute("UPDATE users SET warnings = warnings + 1 WHERE user_id=?", (user_id,))
    conn.commit()

def get_warnings(user_id):
    cursor.execute("SELECT warnings FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0
