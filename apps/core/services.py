"""Бизнес-логика приложения"""
import pandas as pd
from .models import BusinessProcess, Vulnerability, Recommendation

# База ключевых слов для автоматического обнаружения уязвимостей
VULNERABILITY_PATTERNS = {
    'платеж': {
        'title': 'Уязвимость в обработке платежей',
        'description': 'Процесс обрабатывает платежи. Необходимо проверить безопасность передачи данных карт, шифрование, соответствие PCI DSS.',
        'severity': 4,
    },
    'персональные данные': {
        'title': 'Риск утечки персональных данных',
        'description': 'Процесс работает с персональными данными. Требуется проверка защиты от несанкционированного доступа, GDPR compliance.',
        'severity': 5,
    },
    'api': {
        'title': 'Слабая валидация входных данных API',
        'description': 'Процесс использует API. Необходимо проверить валидацию параметров, защиту от SQL injection, XSS.',
        'severity': 4,
    },
    'резервное копирование': {
        'title': 'Проблемы с восстановлением после сбоя',
        'description': 'Процесс включает резервное копирование. Требуется проверка целостности бэкапов и процедур восстановления.',
        'severity': 3,
    },
    'аутентификация': {
        'title': 'Слабая политика паролей',
        'description': 'Процесс требует аутентификацию. Необходимо проверить сложность паролей, MFA, управление сессиями.',
        'severity': 4,
    },
    'логирование': {
        'title': 'Неправильное логирование',
        'description': 'Процесс логирует данные. Важно убедиться, что в логах не сохраняются чувствительные данные.',
        'severity': 3,
    },
    'внешний сервис': {
        'title': 'Риск зависимости от внешнего сервиса',
        'description': 'Процесс зависит от внешнего сервиса. Требуется проверка SLA, fallback механизмов.',
        'severity': 3,
    },
}


def import_processes_from_file(file, user):
    """
    Импортирует процессы из файла (Excel, CSV, JSON).
    Автоматически создает уязвимости на основе ключевых слов.
    
    Returns: (count_created, count_skipped, errors)
    """
    try:
        # Определяем формат и читаем файл
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        elif file.name.endswith('.json'):
            df = pd.read_json(file)
        else:
            return 0, 0, ["Неподдерживаемый формат файла"]

        count_created = 0
        count_skipped = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                # Проверяем наличие обязательного поля 'name'
                if pd.isna(row.get('name')) or row['name'].strip() == '':
                    count_skipped += 1
                    errors.append(f"Строка {idx + 2}: Отсутствует название процесса")
                    continue

                # Создаем процесс
                process = BusinessProcess.objects.create(
                    owner=user,
                    name=str(row['name']).strip(),
                    description=str(row.get('description', '')).strip(),
                    criticality=str(row.get('criticality', 'medium')).lower(),
                    is_active=True
                )

                # Автоматически анализируем описание и создаем уязвимости
                analyze_and_create_vulnerabilities(process, row.get('description', ''))
                
                count_created += 1

            except Exception as e:
                count_skipped += 1
                errors.append(f"Строка {idx + 2}: {str(e)}")

        return count_created, count_skipped, errors

    except Exception as e:
        return 0, 0, [f"Ошибка при чтении файла: {str(e)}"]


def analyze_and_create_vulnerabilities(process, description):
    """
    Анализирует описание процесса и автоматически создает уязвимости
    на основе найденных ключевых слов.
    """
    if not description:
        return

    description_lower = str(description).lower()

    for keyword, vuln_data in VULNERABILITY_PATTERNS.items():
        if keyword in description_lower:
            # Проверяем, не создана ли уже такая уязвимость
            existing = Vulnerability.objects.filter(
                business_process=process,
                title=vuln_data['title']
            ).exists()

            if not existing:
                vuln = Vulnerability.objects.create(
                    business_process=process,
                    title=vuln_data['title'],
                    description=vuln_data['description'],
                    severity=vuln_data['severity'],
                    status='open',
                    is_auto_detected=True
                )

                # Создаем автоматическую рекомендацию
                Recommendation.objects.create(
                    vulnerability=vuln,
                    title=f"Автоматическая рекомендация: {vuln_data['title']}",
                    content="Проведите подробный аудит этого компонента системы. Обратитесь к специалистам по безопасности.",
                    priority=vuln_data['severity']
                )

def calculate_risk_metrics(user):
    """
    Вычисляет основные метрики риска для пользователя.
    Returns: dict с метриками
    """
    vulnerabilities = Vulnerability.objects.filter(business_process__owner=user)
    
    return {
        'total_vulnerabilities': vulnerabilities.count(),
        'critical_count': vulnerabilities.filter(severity=5).count(),
        'high_count': vulnerabilities.filter(severity__in=[3, 4]).count(),
        'resolved_count': vulnerabilities.filter(status='resolved').count(),
        'open_count': vulnerabilities.filter(status='open').count(),
        'in_progress_count': vulnerabilities.filter(status='in_progress').count(),
        'avg_resolution_time': 0, 
    }
