import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

class Config:
    SECRET_KEY = 'your-secret-key-change-in-production'
    JWT_SECRET_KEY = 'jwt-secret-change-me'