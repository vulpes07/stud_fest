import sqlite3
from contextlib import closing

DB_PATH = "bot_db.sqlite3"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT NOT NULL,  
                    age INTEGER NOT NULL,  
                    gender TEXT, 
                    ph_num INTEGER NOT NULL,    
                    latitude REAL,
                    longitude REAL,
                    user_id INTEGER,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT
                        
                );
            """)
            conn.commit()


def is_registered(user_id: int) -> bool:
    return user_id in [user[7] for user in list_users()]


def add_user(name: str, age: int, gender: str, ph_num: int, latitude: float, longitude: float, user_id: int = None, first_name: str = "", last_name: str = "", username: str = ""):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("INSERT INTO users (name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                         (name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username))

def list_users():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        return conn.execute("SELECT id, name, age, gender, ph_num, latitude, longitude, user_id, first_name, last_name, username FROM users").fetchall()

def remove_user(id: int):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with conn:
            conn.execute("DELETE FROM users WHERE id = ?", (id,))
