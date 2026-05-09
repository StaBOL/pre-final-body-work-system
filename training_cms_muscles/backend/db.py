import os
import psycopg2
import psycopg2.extras
from flask import g
from backend.config import Config

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
        g.db.autocommit = False
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db:
        db.close()

def query_one(sql, params=()):
    cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return row

def query_all(sql, params=()):
    cur = get_db().cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return rows

def execute(sql, params=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    last_id = cur.fetchone()
    cur.close()
    return last_id[0] if last_id else None
