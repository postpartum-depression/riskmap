import os
import django
import random
from datetime import timedelta, date

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riskmap.settings') # Проверь, что папка с settings.py называется config или core
django.setup()

from django.contrib.auth import get_user_model
from apps.core.models import BusinessProcess, Vulnerability, Recommendation

User = get_user_model()

def create_demo_data():
    # 1. Получаем или создаем пользователя для теста
    username = "admin"  # Можешь поменять на своего юзера
    user = User.objects.filter(username=username).first()
    
    if not user:
        print(f"❌ Пользователь {username} не найден! Создайте его сначала или укажите существующего.")
        return

    print(f"👤 Используем пользователя: {user.username}")

    # 2. Создаем Бизнес-процесс
    bp_name = "Процесс Онлайн-оплаты (E-commerce)"
    
    # Удаляем старый, если запускаешь скрипт повторно, чтобы не плодить дубли
    BusinessProcess.objects.filter(name=bp_name, owner=user).delete()
    
    bp = BusinessProcess.objects.create(
        name=bp_name,
        description="Обработка платежей клиентов через шлюз, сохранение токенов карт, формирование чеков.",
        owner=user,
        criticality='critical'
    )
    print(f"✅ Создан процесс: {bp.name}")

    # 3. Список типовых уязвимостей для этого процесса
    vulnerabilities_data = [
        {
            "title": "Хранение CVV кодов в логах",
            "desc": "При отладке шлюза в лог-файлы сервера записываются полные данные карт, включая CVV.",
            "severity": 5, # Критическая
            "status": "open"
        },
        {
            "title": "Отсутствие шифрования при передаче данных",
            "desc": "Внутренний обмен данными между сервисом биллинга и базой идет по HTTP.",
            "severity": 4, # Высокая
            "status": "in_progress"
        },
        {
            "title": "Устаревшая версия библиотеки OpenSSL",
            "desc": "Сервер использует версию OpenSSL с известными CVE.",
            "severity": 3, # Средняя
            "status": "resolved"
        },
        {
            "title": "Слабая парольная политика для админов",
            "desc": "Допускаются пароли длиной 6 символов без спецзнаков.",
            "severity": 2, # Низкая
            "status": "open"
        },
        {
            "title": "Открытый порт базы данных во вне",
            "desc": "Порт 5432 доступен из интернета для всех IP.",
            "severity": 5, # Критическая
            "status": "closed"
        }
    ]

    # 4. Создаем уязвимости
    for v_data in vulnerabilities_data:
        vuln = Vulnerability.objects.create(
            business_process=bp,
            title=v_data["title"],
            description=v_data["desc"],
            severity=v_data["severity"],
            status=v_data["status"],
            discovered_date=date.today() - timedelta(days=random.randint(1, 30))
        )
        print(f"   🔸 Добавлена уязвимость: {vuln.title} ({vuln.get_status_display()})")

        # 5. Добавляем рекомендацию к каждой уязвимости
        Recommendation.objects.create(
            vulnerability=vuln,
            title=f"Рекомендация по устранению: {vuln.title}",
            content="Необходимо провести аудит конфигурации и обновить ПО до стабильной версии. Настроить фильтрацию логов.",
            priority=3 if v_data['severity'] > 3 else 2
        )

    print("\n🚀 Демо-данные успешно загружены! Обновите дашборд.")

if __name__ == '__main__':
    create_demo_data()
