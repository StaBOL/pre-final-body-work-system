from flask import Flask, redirect
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.db import close_db, init_db

def create_app():
    # static_folder='frontend' — Flask сам раздаст все файлы из этой папки
    app = Flask(__name__, static_folder='frontend')
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

    # Редирект с корня на index.html
    @app.route('/')
    def index():
        return redirect('/index.html')

    # Диагностический маршрут (можно удалить позже)
    @app.route('/check')
    def check():
        import os
        return {
            'cwd': os.getcwd(),
            'frontend_exists': os.path.exists('frontend'),
            'index_exists': os.path.exists('frontend/index.html')
        }

    return app

application = create_app()

with application.app_context():
    init_db()
