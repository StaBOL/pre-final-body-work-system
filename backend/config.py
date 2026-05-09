import os

# Определяем BASE_DIR как корневую директорию проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Путь к файлу базы данных SQLite
DB_PATH = os.path.join(BASE_DIR, 'database.db')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret')
    # Адрес базы данных для production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}').replace('postgres://', 'postgresql://')
