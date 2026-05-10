from flask import Flask
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.db import close_db, init_db
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    JWTManager(app)

    app.teardown_appcontext(close_db)

    from backend.auth import register, login
    from backend.api import (
        get_muscle_groups, get_exercises, get_exercise,
        create_workout, get_my_workouts, get_workout, log_set, delete_workout
    )

    app.add_url_rule('/api/register', view_func=register, methods=['POST'])
    app.add_url_rule('/api/login', view_func=login, methods=['POST'])
    app.add_url_rule('/api/muscle-groups', view_func=get_muscle_groups, methods=['GET'])
    app.add_url_rule('/api/exercises', view_func=get_exercises, methods=['GET'])
    app.add_url_rule('/api/exercises/<int:exercise_id>', view_func=get_exercise, methods=['GET'])
    app.add_url_rule('/api/workouts', view_func=create_workout, methods=['POST'])
    app.add_url_rule('/api/workouts', view_func=get_my_workouts, methods=['GET'])
    app.add_url_rule('/api/workouts/<int:workout_id>', view_func=get_workout, methods=['GET'])
    app.add_url_rule('/api/workout-exercises/<int:workout_exercise_id>/log', view_func=log_set, methods=['POST'])
    app.add_url_rule('/api/workouts/<int:workout_id>', view_func=delete_workout, methods=['DELETE'])

    # Главная страница – читаем index.html напрямую
    @app.route('/')
    def index():
        index_path = os.path.join('frontend', 'index.html')
        if not os.path.exists(index_path):
            return f"File not found: {index_path}", 404
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()

    # Все остальные статические файлы (CSS, JS, другие HTML)
    @app.route('/<path:path>')
    def static_files(path):
        file_path = os.path.join('frontend', path)
        if not os.path.exists(file_path):
            return f"File not found: {file_path}", 404
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    # Диагностика
    @app.route('/check')
    def check():
        return {
            'cwd': os.getcwd(),
            'frontend_exists': os.path.exists('frontend'),
            'index_exists': os.path.exists(os.path.join('frontend', 'index.html'))
        }

    @app.route('/ls-frontend')
    def ls_frontend():
        try:
            files = os.listdir('frontend') if os.path.exists('frontend') else []
            return {'files': files}
        except Exception as e:
            return {'error': str(e)}, 500

    return app

application = create_app()

with application.app_context():
    init_db()
