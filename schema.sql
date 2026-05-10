-- Таблица пользователей
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'student'
);

-- Группы мышц
CREATE TABLE IF NOT EXISTS muscle_group (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    photo_url TEXT
);

-- Упражнения
CREATE TABLE IF NOT EXISTS exercise (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    technique TEXT,
    difficulty TEXT DEFAULT 'medium',
    photo_url TEXT,
    muscle_group_id INTEGER NOT NULL REFERENCES muscle_group(id) ON DELETE CASCADE
);

-- Тренировки
CREATE TABLE IF NOT EXISTS workout (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE
);

-- Связь тренировки и упражнения
CREATE TABLE IF NOT EXISTS workout_exercise (
    id SERIAL PRIMARY KEY,
    workout_id INTEGER NOT NULL REFERENCES workout(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercise(id) ON DELETE CASCADE,
    sets INTEGER DEFAULT 3,
    reps INTEGER DEFAULT 10,
    weight REAL,
    "order" INTEGER DEFAULT 0
);

-- Логи выполнения подходов
CREATE TABLE IF NOT EXISTS workout_log (
    id SERIAL PRIMARY KEY,
    workout_exercise_id INTEGER NOT NULL REFERENCES workout_exercise(id) ON DELETE CASCADE,
    set_number INTEGER,
    reps_done INTEGER,
    weight_used REAL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы (опционально)
CREATE INDEX IF NOT EXISTS idx_exercise_muscle ON exercise(muscle_group_id);
CREATE INDEX IF NOT EXISTS idx_workout_user ON workout(user_id);
CREATE INDEX IF NOT EXISTS idx_workoutex_workout ON workout_exercise(workout_id);
CREATE INDEX IF NOT EXISTS idx_workoutlog_workoutex ON workout_log(workout_exercise_id);
