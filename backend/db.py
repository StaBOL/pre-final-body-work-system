import os
import psycopg
from flask import g
from backend.config import Config

def get_db():
    if 'db' not in g:
        # Подключаемся к PostgreSQL, используя URI из конфига
        g.db = psycopg.connect(Config.SQLALCHEMY_DATABASE_URI)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
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
        # Пытаемся получить последний ID, если операция - вставка
        try:
            return cur.fetchone()[0]
        except:
            return None

def init_db():
    """Создаёт таблицы, если их нет, используя schema.sql."""
    conn = get_db()
    with conn.cursor() as cur:
        # Читаем и выполняем schema.sql
        with open(os.path.join(BASE_DIR, 'schema.sql'), 'r', encoding='utf-8') as f:
            cur.execute(f.read())
    conn.commit()
