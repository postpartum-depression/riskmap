from django.core.management.base import BaseCommand
from apps.core.models import VulnerabilityTemplate

class Command(BaseCommand):
    help = 'Загружает банковские шаблоны с рекомендациями'

    def handle(self, *args, **kwargs):
        # Очистим старые, чтобы обновить данные
        VulnerabilityTemplate.objects.all().delete()

        templates = [
            # --- ШАГ 1: Ввод email ---
            {
                "title": "Email Enumeration",
                "description": "Система выдает разные ответы для существующих и несуществующих email-адресов. Это позволяет собрать базу клиентов.",
                "severity": 2,
                "keywords": "email, ввод почты, регистрация",
                "mitigation": "Используйте одинаковые сообщения для всех случаев. Например: 'Если такой адрес существует, мы отправили на него письмо'. Не возвращайте ошибки 'Email не найден' или 'Email занят' явно."
            },
            {
                "title": "No Rate Limiting on Registration",
                "description": "Отсутствует ограничение на количество запросов. Возможен DoS или email-бомбинг.",
                "severity": 3,
                "keywords": "регистрация, ввод email, форма",
                "mitigation": "1. Внедрите капчу (Google reCAPTCHA или аналог). 2. Настройте Rate Limiting (например, не более 5 попыток с одного IP в минуту). 3. Используйте Double Opt-In."
            },
            
            # --- ШАГ 2: Ссылка подтверждения ---
            {
                "title": "Token Leakage via Referer",
                "description": "Токен в URL может утечь через заголовок Referer при переходе по внешним ссылкам.",
                "severity": 4,
                "keywords": "ссылка, подтверждение, переход, confirm",
                "mitigation": "Настройте политику Referrer-Policy: 'no-referrer' или 'same-origin' на страницах с токенами. Избегайте размещения внешних ссылок на страницах сброса пароля или подтверждения."
            },
            {
                "title": "Lack of Token Expiration",
                "description": "Ссылка подтверждения живет слишком долго, риск перехвата.",
                "severity": 3,
                "keywords": "ссылка, подтверждение, токен",
                "mitigation": "Установите короткий срок жизни токена (например, 15-30 минут). После использования токен должен немедленно аннулироваться."
            },

            # --- ШАГ 3: Загрузка сканов ---
            {
                "title": "Unrestricted File Upload (RCE)",
                "description": "Загрузка файлов без проверки содержимого. Возможность загрузки веб-шеллов.",
                "severity": 5,
                "keywords": "загрузка, скан, файл, upload",
                "mitigation": "1. Проверяйте MIME-type и Magic Numbers (сигнатуры) файла, а не только расширение. 2. Переименовывайте файлы при сохранении (генерируйте случайное имя). 3. Храните файлы вне корневой директории веб-сервера."
            },
            {
                "title": "No Virus Scan on Uploads",
                "description": "Загружаемые файлы не проверяются антивирусом.",
                "severity": 4,
                "keywords": "загрузка, скан, файл, upload",
                "mitigation": "Интегрируйте антивирусное решение (например, ClamAV) в пайплайн загрузки файлов. Сканируйте файлы в песочнице перед сохранением."
            },

            # --- ШАГ 4: Проверка оператором ---
            {
                "title": "Blind XSS in Admin Panel",
                "description": "Данные анкеты не экранируются в админке. Риск выполнения JS-кода у оператора.",
                "severity": 4,
                "keywords": "проверка, оператор, админка, документы",
                "mitigation": "Обязательно экранируйте все данные, полученные от пользователя, при выводе в админ-панель. Используйте Content Security Policy (CSP), чтобы запретить выполнение сторонних скриптов."
            },

            # --- ШАГ 5: Создание учетки ---
            {
                "title": "Predictable User ID (IDOR)",
                "description": "Предсказуемые ID пользователей позволяют перебирать чужие профили.",
                "severity": 4,
                "keywords": "создание, учетная запись, аккаунт, user",
                "mitigation": "Используйте UUID (GUID) вместо последовательных числовых ID (1, 2, 3...). Внедрите строгую проверку прав доступа (ACL) при каждом обращении к объекту пользователя."
            },
            {
                "title": "Default Password Weakness",
                "description": "Генерация слабого пароля и отправка его в открытом виде.",
                "severity": 3,
                "keywords": "пароль, создание, password",
                "mitigation": "Никогда не генерируйте пароли за пользователя. Отправляйте ссылку на установку пароля. Если генерация необходима, требуйте смены пароля при первом входе."
            }
        ]

        for t in templates:
            VulnerabilityTemplate.objects.create(
                title=t['title'],
                description=t['description'],
                severity=t['severity'],
                keywords=t['keywords'],
                mitigation=t['mitigation']
            )

        self.stdout.write(self.style.SUCCESS(f'База обновлена! Загружено {len(templates)} шаблонов с рекомендациями.'))
