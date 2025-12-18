import pandas as pd
from .models import BusinessProcess, Vulnerability, Recommendation, VulnerabilityTemplate

def import_processes_from_file(file, user):
    """
    Импортирует процессы из файла (Excel, CSV, JSON).
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
                
                # --- ЗАПУСКАЕМ АВТО-АНАЛИЗ ---
                auto_scan_process(process)
                # -----------------------------
                
                count_created += 1

            except Exception as e:
                count_skipped += 1
                errors.append(f"Строка {idx + 2}: {str(e)}")

        return count_created, count_skipped, errors

    except Exception as e:
        return 0, 0, [f"Ошибка при чтении файла: {str(e)}"]


def auto_scan_process(process):
    """
    Анализирует шаги процесса (и описание процесса) и создает уязвимости
    на основе шаблонов из базы данных.
    """
    found_vulns = []
    
    # 1. Получаем все шаблоны из БД
    templates = VulnerabilityTemplate.objects.all()
    
    # 2. Собираем тексты для анализа: Название процесса + Описание процесса
    #    А также будем проходить по каждому шагу отдельно
    
    # --- АНАЛИЗ ШАГОВ (более точный) ---
    for step in process.steps.all():
        step_text = step.name.lower() + " " + step.description.lower()
        
        for template in templates:
            # Разбиваем ключевые слова
            keywords = [k.strip().lower() for k in template.keywords.split(',')]
            
            # Если ключевое слово найдено в названии/описании ШАГА
            if any(keyword in step_text for keyword in keywords):
                
                # Проверяем дубликаты на этом шаге
                exists = Vulnerability.objects.filter(
                    business_process=process,
                    step=step,
                    title=template.title
                ).exists()
                
                if not exists:
                    # Создаем уязвимость
                    vuln = Vulnerability.objects.create(
                        business_process=process,
                        step=step,
                        title=template.title,
                        description=template.description,
                        severity=template.severity,
                        status='open'
                    )
                    
                    # Создаем рекомендацию
                    if template.mitigation:
                        Recommendation.objects.create(
                            vulnerability=vuln,
                            title=f"Решение: {template.title}",
                            content=template.mitigation,
                            priority=3
                        )
                    
                    found_vulns.append(vuln)

    return found_vulns


def calculate_risk_metrics(user):
    """
    Вычисляет основные метрики риска для пользователя.
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
