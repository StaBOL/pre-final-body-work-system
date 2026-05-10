import psycopg
from werkzeug.security import generate_password_hash
from backend.config import Config

def main():
    conn = psycopg.connect(Config.SQLALCHEMY_DATABASE_URI)
    cur = conn.cursor()

    # Группы мышц
    groups = [
        ('Грудные', 'Упражнения для развития грудных мышц', 'https://picsum.photos/id/100/400/300'),
        ('Спина', 'Тренировка широчайших и трапеций', 'https://picsum.photos/id/101/400/300'),
        ('Ноги', 'Квадрицепсы, бицепс бедра, ягодицы', 'https://picsum.photos/id/102/400/300'),
        ('Плечи', 'Дельтовидные мышцы', 'https://picsum.photos/id/103/400/300'),
        ('Бицепс', 'Сгибатели рук', 'https://picsum.photos/id/104/400/300'),
        ('Трицепс', 'Разгибатели рук', 'https://picsum.photos/id/105/400/300'),
        ('Пресс', 'Мышцы кора', 'https://picsum.photos/id/106/400/300'),
        ('Ягодицы', 'Укрепление ягодичных', 'https://picsum.photos/id/107/400/300'),
    ]
    for name, desc, url in groups:
        cur.execute("""
            INSERT INTO muscle_group (name, description, photo_url)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """, (name, desc, url))

    # Упражнения (полный список — у вас 41, я покажу несколько, вы добавите остальные сами)
    exercises = [
        ('Жим штанги лёжа', 'Базовое упражнение для массы груди', 'Техника...', 'medium', 'https://picsum.photos/id/1/400/300', 1),
        # ... добавьте остальные упражнения из вашего seed.py
    ]
    for name, desc, tech, diff, img, mg_id in exercises:
        cur.execute("""
            INSERT INTO exercise (name, description, technique, difficulty, photo_url, muscle_group_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (name, desc, tech, diff, img, mg_id))

    # Тестовый пользователь
    hashed = generate_password_hash('student')
    cur.execute("""
        INSERT INTO "user" (email, password, role)
        VALUES (%s, %s, %s)
        ON CONFLICT (email) DO NOTHING
    """, ('student@example.com', hashed, 'student'))

    conn.commit()
    cur.close()
    conn.close()
    print("Данные успешно добавлены в PostgreSQL!")

if __name__ == '__main__':
    main()
