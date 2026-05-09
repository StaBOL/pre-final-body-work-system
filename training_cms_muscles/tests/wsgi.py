# wsgi.py
from backend.app import create_app

# Создаем экземпляр приложения.
# Переменная должна называться 'application', так как
# Gunicorn ищет по умолчанию именно её.
application = create_app()
