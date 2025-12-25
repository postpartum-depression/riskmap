from .models import BusinessProcess, Vulnerability, Recommendation, VulnerabilityTemplate

def auto_scan_process(process):
    """
    Анализирует шаги процесса (и описание процесса) и создает уязвимости
    на основе шаблонов из базы данных.
    """
    found_vulns = []
    
    # 1. Получаем все шаблоны из БД
    templates = VulnerabilityTemplate.objects.all()
    
    # 2. Собираем тексты для анализа: Название процесса + Описание процесса

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
