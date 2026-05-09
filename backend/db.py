import sqlite3
import os
from flask import g
from backend.config import BASE_DIR, DB_PATH

# --- Функции для работы внутри запросов Flask (с g) ---
def get_db():
    """Возвращает соединение с БД (для каждого запроса своё)."""
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_one(sql, params=()):
    cur = get_db().execute(sql, params)
    return cur.fetchone()

def query_all(sql, params=()):
    cur = get_db().execute(sql, params)
    return cur.fetchall()

def execute(sql, params=()):
    cur = get_db().execute(sql, params)
    get_db().commit()
    return cur.lastrowid

# --- Функция для инициализации БД (без g, работает вне приложения) ---
def init_db():
    """Создаёт таблицы, если их нет, используя schema.sql."""
    conn = sqlite3.connect(DB_PATH)
    with open(os.path.join(BASE_DIR, 'schema.sql'), 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()