import os
import psycopg
from flask import g
from backend.config import Config, BASE_DIR   # <-- добавили BASE_DIR

def get_db():
    if 'db' not in g:
        g.db = psycopg.connect(Config.SQLALCHEMY_DATABASE_URI)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()

def query_one(sql, params=()):
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
    return row

def query_all(sql, params=()):
    with get_db().cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    return rows

def execute(sql, params=()):
    conn = get_db()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        conn.commit()
        try:
            return cur.fetchone()[0]
        except:
            return None

def init_db():
    """Создаёт таблицы, если их нет, используя schema.sql."""
    conn = get_db()
    schema_path = os.path.join(BASE_DIR, 'schema.sql')
    if not os.path.exists(schema_path):
        print(f"Schema file not found at {schema_path}")
        return
    with conn.cursor() as cur:
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql = f.read()
        cur.execute(sql)
    conn.commit()
    print("Database initialized successfully")
