from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# 1. СНАЧАЛА БИЗНЕС-ПРОЦЕСС
class BusinessProcess(models.Model):
    """Модель бизнес-процесса"""
    
    CRITICALITY_CHOICES = [
        ('low', 'Низкая'),
        ('medium', 'Средняя'),
        ('high', 'Высокая'),
        ('critical', 'Критическая'),
    ]
    
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='business_processes',
        verbose_name='Владелец'
    )
    criticality = models.CharField(
        'Критичность',
        max_length=20,
        choices=CRITICALITY_CHOICES,
        default='medium'
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_active = models.BooleanField('Активен', default=True)
    
    class Meta:
        verbose_name = 'Бизнес-процесс'
        verbose_name_plural = 'Бизнес-процессы'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def vulnerability_count(self):
        """Количество уязвимостей"""
        return self.vulnerabilities.count()
    
    @property
    def risk_score(self):
        """Общий уровень риска"""
        vulnerabilities = self.vulnerabilities.all()
        if not vulnerabilities:
            return 0
        return sum(v.severity_score for v in vulnerabilities) / len(vulnerabilities)


# 2. ПОТОМ ШАГИ (ProcessStep)
class ProcessStep(models.Model):
    """Шаг (этап) бизнес-процесса"""
    business_process = models.ForeignKey(BusinessProcess, on_delete=models.CASCADE, related_name='steps')
    name = models.CharField(max_length=100, verbose_name="Название шага")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    color = models.CharField(
        max_length=20, 
        default='primary',
        choices=[
            ('primary', 'Синий'),
            ('danger', 'Красный'),
            ('warning', 'Желтый'),
            ('success', 'Зеленый'),
            ('info', 'Голубой'),
        ],
        verbose_name="Цвет"
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Шаг процесса"
        verbose_name_plural = "Шаги процесса"

    def __str__(self):
        return f"{self.name} ({self.business_process.name})"


# 3. ПОТОМ УЯЗВИМОСТЬ (Знает про BusinessProcess и ProcessStep)
class Vulnerability(models.Model):
    """Модель уязвимости"""
    
    SEVERITY_CHOICES = [
        (1, 'Незначительная'),
        (2, 'Низкая'),
        (3, 'Средняя'),
        (4, 'Высокая'),
        (5, 'Критическая'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Открыта'),
        ('in_progress', 'В работе'),
        ('resolved', 'Решена'),
        ('closed', 'Закрыта'),
    ]
    
    business_process = models.ForeignKey(
        BusinessProcess,
        on_delete=models.CASCADE,
        related_name='vulnerabilities',
        verbose_name='Бизнес-процесс'
    )

    # Связь с шагом
    step = models.ForeignKey(
        ProcessStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vulnerabilities',
        verbose_name='Связанный шаг'
    )

    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    severity = models.IntegerField('Уровень серьезности', choices=SEVERITY_CHOICES, default=3)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='open')
    discovered_date = models.DateField('Дата обнаружения', auto_now_add=True)
    resolved_date = models.DateField('Дата решения', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Уязвимость'
        verbose_name_plural = 'Уязвимости'
        ordering = ['-severity', '-discovered_date']
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()})"
    
    @property
    def severity_score(self):
        """Оценка серьезности от 0 до 100"""
        return self.severity * 20


# 4. ПОТОМ РЕКОМЕНДАЦИИ (Знает про Vulnerability)
class Recommendation(models.Model):
    """Модель рекомендации"""
    
    PRIORITY_CHOICES = [
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
    ]
    
    vulnerability = models.ForeignKey(
        Vulnerability,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='Уязвимость'
    )
    title = models.CharField('Заголовок', max_length=255)
    content = models.TextField('Содержание')
    priority = models.IntegerField('Приоритет', choices=PRIORITY_CHOICES, default=2)
    is_implemented = models.BooleanField('Выполнено', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Рекомендация'
        verbose_name_plural = 'Рекомендации'
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title


# 5. ПОТОМ ЛОГИ (Знает про Vulnerability)
class AuditLog(models.Model):
    """Логирование всех изменений уязвимостей"""
    
    ACTION_CHOICES = [
        ('created', 'Создана'),
        ('status_changed', 'Изменен статус'),
        ('assigned', 'Назначена'),
        ('description_changed', 'Изменено описание'),
        ('resolved', 'Решена'),
    ]
    
    vulnerability = models.ForeignKey(
        Vulnerability,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name='Уязвимость'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Пользователь'
    )
    action = models.CharField('Действие', max_length=50, choices=ACTION_CHOICES)
    old_value = models.TextField('Старое значение', blank=True, null=True)
    new_value = models.TextField('Новое значение', blank=True, null=True)
    timestamp = models.DateTimeField('Время', auto_now_add=True)
    comment = models.TextField('Комментарий', blank=True)

    class Meta:
        verbose_name = 'Лог аудита'
        verbose_name_plural = 'Логи аудита'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.vulnerability.title} - {self.get_action_display()} ({self.timestamp})"
    
    # 6. БАНК УЯЗВИМОСТЕЙ (Новая модель для авто-подбора)
class VulnerabilityTemplate(models.Model):
    """Шаблон уязвимости для базы знаний"""
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание')
    severity = models.IntegerField(
        'Базовая серьезность', 
        choices=Vulnerability.SEVERITY_CHOICES, 
        default=3
    )
    
    # Ключевые слова для поиска (например: "вход, login, auth")
    keywords = models.TextField('Ключевые слова', help_text="Слова через запятую для авто-поиска")
    
    # Рекомендация по умолчанию
    mitigation = models.TextField('Рекомендация по устранению', blank=True, help_text="Шаблон решения проблемы")

    class Meta:
        verbose_name = 'Шаблон уязвимости'
        verbose_name_plural = 'Банк уязвимостей'

    def __str__(self):
        return self.title


