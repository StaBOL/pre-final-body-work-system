from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.db import get_db, query_one, query_all, execute

def get_muscle_groups():
    rows = query_all('SELECT id, name, photo_url FROM muscle_group')
    return jsonify([dict(row) for row in rows])

def get_exercises():
    muscle_id = request.args.get('muscle', type=int)
    if muscle_id:
        rows = query_all('SELECT id, name, difficulty, photo_url, muscle_group_id, description FROM exercise WHERE muscle_group_id = ?', (muscle_id,))
    else:
        rows = query_all('SELECT id, name, difficulty, photo_url, muscle_group_id, description FROM exercise')
    return jsonify([dict(row) for row in rows])

def get_exercise(exercise_id):
    row = query_one('SELECT id, name, description, technique, difficulty, photo_url, muscle_group_id FROM exercise WHERE id = ?', (exercise_id,))
    if not row:
        return jsonify({'msg': 'Not found'}), 404
    return jsonify(dict(row))

@jwt_required()
def create_workout():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get('name')
    exercises = data.get('exercises', [])
    if not name:
        return jsonify({'msg': 'Workout name required'}), 400
    db = get_db()
    workout_id = execute('INSERT INTO workout (name, user_id) VALUES (?, ?)', (name, user_id))
    for idx, ex in enumerate(exercises):
        execute('''INSERT INTO workout_exercise (workout_id, exercise_id, sets, reps, weight, "order")
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (workout_id, ex['exercise_id'], ex.get('sets', 3), ex.get('reps', 10), ex.get('weight'), idx))
    return jsonify({'id': workout_id, 'msg': 'Workout created'}), 201

@jwt_required()
def get_my_workouts():
    user_id = int(get_jwt_identity())
    rows = query_all('SELECT id, name, created_at FROM workout WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    return jsonify([{'id': r['id'], 'name': r['name'], 'created_at': r['created_at']} for r in rows])

@jwt_required()
def get_workout(workout_id):
    user_id = int(get_jwt_identity())
    workout = query_one('SELECT id, name, user_id FROM workout WHERE id = ?', (workout_id,))
    if not workout or workout['user_id'] != user_id:
        return jsonify({'msg': 'Unauthorized'}), 403
    we_rows = query_all('''
        SELECT we.id, we.sets, we.reps, we.weight, we."order",
               e.id as exercise_id, e.name, e.photo_url
        FROM workout_exercise we
        JOIN exercise e ON we.exercise_id = e.id
        WHERE we.workout_id = ?
        ORDER BY we."order"
    ''', (workout_id,))
    exercises = []
    for row in we_rows:
        exercises.append({
            'id': row['id'],
            'exercise_id': row['exercise_id'],
            'name': row['name'],
            'photo_url': row['photo_url'],
            'sets': row['sets'],
            'reps': row['reps'],
            'weight': row['weight'],
            'order': row['order']
        })
    return jsonify({'id': workout['id'], 'name': workout['name'], 'exercises': exercises})

@jwt_required()
def log_set(workout_exercise_id):
    user_id = int(get_jwt_identity())
    # Проверка, что эта связь принадлежит тренировке текущего пользователя
    we = query_one('''
        SELECT we.id FROM workout_exercise we
        JOIN workout w ON we.workout_id = w.id
        WHERE we.id = ? AND w.user_id = ?
    ''', (workout_exercise_id, user_id))
    if not we:
        return jsonify({'msg': 'Unauthorized'}), 403
    data = request.get_json()
    execute('''INSERT INTO workout_log (workout_exercise_id, set_number, reps_done, weight_used)
               VALUES (?, ?, ?, ?)''',
            (workout_exercise_id, data.get('set_number'), data.get('reps_done'), data.get('weight_used')))
    return jsonify({'msg': 'Set logged'}), 201

@jwt_required()
def delete_workout(workout_id):
    user_id = int(get_jwt_identity())
    # Проверим, принадлежит ли тренировка пользователю
    workout = query_one('SELECT id FROM workout WHERE id = ? AND user_id = ?', (workout_id, user_id))
    if not workout:
        return jsonify({'msg': 'Workout not found or unauthorized'}), 404
    execute('DELETE FROM workout WHERE id = ?', (workout_id,))
    return jsonify({'msg': 'Workout deleted'}), 200
    from werkzeug.security import generate_password_hash

def seed_database():
    import psycopg
    from backend.config import Config
    conn = psycopg.connect(Config.SQLALCHEMY_DATABASE_URI)
    cur = conn.cursor()
    
    # Группы мышц (если пусто)
    groups = [
        ('Грудные', 'Упражнения для груди', 'https://picsum.photos/id/100/400/300'),
        ('Спина', 'Упражнения для спины', 'https://picsum.photos/id/101/400/300'),
        ('Ноги', 'Упражнения для ног', 'https://picsum.photos/id/102/400/300'),
        ('Плечи', 'Упражнения для плеч', 'https://picsum.photos/id/103/400/300'),
        ('Бицепс', 'Упражнения для бицепса', 'https://picsum.photos/id/104/400/300'),
        ('Трицепс', 'Упражнения для трицепса', 'https://picsum.photos/id/105/400/300'),
        ('Пресс', 'Упражнения для пресса', 'https://picsum.photos/id/106/400/300'),
        ('Ягодицы', 'Упражнения для ягодиц', 'https://picsum.photos/id/107/400/300'),
    ]
    for g in groups:
        cur.execute("INSERT INTO muscle_group (name, description, photo_url) VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING", g)
    
    # Упражнения
    exercises = [
        ('Жим штанги лёжа', 'Базовое упражнение для грудных', 'Лёжа на скамье, опускайте гриф к груди, выжимайте вверх.', 'medium', 'https://picsum.photos/id/1/400/300', 1),
        ('Отжимания на брусьях', 'Работает низ груди и трицепс', 'Наклон корпуса вперёд для акцента на грудь.', 'hard', 'https://picsum.photos/id/3/400/300', 1),
        ('Тяга штанги в наклоне', 'Развитие широчайших', 'Наклон 45°, тяните к поясу.', 'medium', 'https://picsum.photos/id/6/400/300', 2),
        ('Подтягивания', 'Классика спины', 'Широкий хват к груди.', 'hard', 'https://picsum.photos/id/10/400/300', 2),
        ('Приседания со штангой', 'Основа для ног', 'Спина прямая, колени не выходят за носки.', 'medium', 'https://picsum.photos/id/12/400/300', 3),
        ('Выпады с гантелями', 'Ягодицы и квадрицепс', 'Шаг вперёд, следите за коленом.', 'medium', 'https://picsum.photos/id/16/400/300', 3),
        ('Жим штанги сидя', 'Передние дельты', 'Опускайте гриф к ключицам.', 'medium', 'https://picsum.photos/id/18/400/300', 4),
        ('Разведение гантелей в стороны', 'Средняя дельта', 'Лёгкий вес, локти чуть согнуты.', 'easy', 'https://picsum.photos/id/20/400/300', 4),
        ('Подъём штанги на бицепс', 'Изоляция бицепса', 'Локти прижаты, не раскачивайтесь.', 'easy', 'https://picsum.photos/id/23/400/300', 5),
        ('Французский жим лёжа', 'Трицепс', 'Штанга за головой, опускайте ко лбу.', 'medium', 'https://picsum.photos/id/28/400/300', 6),
        ('Скручивания на полу', 'Верхний пресс', 'Поясница прижата, скручивайте корпус.', 'easy', 'https://picsum.photos/id/33/400/300', 7),
        ('Планка', 'Статика кора', 'Держите тело ровно.', 'easy', 'https://picsum.photos/id/36/400/300', 7),
        ('Ягодичный мост', 'Начальный уровень', 'Поднимайте таз вверх, сжимая ягодицы.', 'easy', 'https://picsum.photos/id/38/400/300', 8),
    ]
    for ex in exercises:
        cur.execute("""INSERT INTO exercise (name, description, technique, difficulty, photo_url, muscle_group_id)
                      VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""", ex)
    
    # Тестовый пользователь
    hashed = generate_password_hash('student')
    cur.execute("INSERT INTO \"user\" (email, password, role) VALUES (%s, %s, %s) ON CONFLICT (email) DO NOTHING",
                ('student@example.com', hashed, 'student'))
    
    # Базовые тренировки (пример) – для пользователя student
    user_id = cur.execute("SELECT id FROM \"user\" WHERE email = 'student@example.com'").fetchone()
    if user_id:
        user_id = user_id[0]
        # Тренировка "Грудь+трицепс"
        cur.execute("INSERT INTO workout (name, user_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", ('Грудь + трицепс', user_id))
        workout_id = cur.execute("SELECT id FROM workout WHERE name = 'Грудь + трицепс' AND user_id = %s", (user_id,)).fetchone()
        if workout_id:
            workout_id = workout_id[0]
            # Получаем id упражнений
            cur.execute("SELECT id FROM exercise WHERE name = 'Жим штанги лёжа'")
            ex1 = cur.fetchone()
            cur.execute("SELECT id FROM exercise WHERE name = 'Отжимания на брусьях'")
            ex2 = cur.fetchone()
            cur.execute("SELECT id FROM exercise WHERE name = 'Французский жим лёжа'")
            ex3 = cur.fetchone()
            if ex1: cur.execute("INSERT INTO workout_exercise (workout_id, exercise_id, sets, reps, \"order\") VALUES (%s, %s, 4, 10, 1)", (workout_id, ex1[0]))
            if ex2: cur.execute("INSERT INTO workout_exercise (workout_id, exercise_id, sets, reps, \"order\") VALUES (%s, %s, 3, 12, 2)", (workout_id, ex2[0]))
            if ex3: cur.execute("INSERT INTO workout_exercise (workout_id, exercise_id, sets, reps, \"order\") VALUES (%s, %s, 3, 12, 3)", (workout_id, ex3[0]))
    
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Database seeded with exercises and sample workout"}
