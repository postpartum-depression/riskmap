# 1. Создаем виртуальное окружение
python -m venv venv

# 2. Активируем его
.\venv\Scripts\Activate

# Если ошибка активации, введите эту команду и попробуйте снова:
# Set-ExecutionPolicy RemoteSigned -Scope Process

# 3. Обновляем pip и устанавливаем библиотеки
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Применяем миграции (создаем таблицы)
python manage.py migrate

# 5. Создаем администратора (Superuser)
python manage.py createsuperuser

# 6. Запуск проекта
python manage.py runserver

Главная: http://127.0.0.1:8000/

Админка: http://127.0.0.1:8000/admin/