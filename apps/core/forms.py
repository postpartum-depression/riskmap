from django import forms
from .models import BusinessProcess, Vulnerability, Recommendation, AuditLog
from .models import ProcessStep


class BusinessProcessForm(forms.ModelForm):
    """Форма для создания/редактирования процесса"""
    class Meta:
        model = BusinessProcess
        fields = ['name', 'description', 'criticality', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'criticality': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class VulnerabilityForm(forms.ModelForm):
    class Meta:
        model = Vulnerability
        fields = ['title', 'description', 'severity', 'status', 'step']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'step': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'step': 'Связанный шаг процесса (необязательно)'
        }

    def __init__(self, *args, **kwargs):
        # 1. Забираем process_id, чтобы он не попал в super()
        process_id = kwargs.pop('process_id', None)
        
        # 2. Вызываем родительский __init__ без process_id
        super().__init__(*args, **kwargs)
        
        # 3. Фильтруем шаги
        if process_id:
            self.fields['step'].queryset = ProcessStep.objects.filter(business_process_id=process_id)
        elif self.instance.pk and self.instance.business_process:
            self.fields['step'].queryset = self.instance.business_process.steps.all()
        else:
            self.fields['step'].queryset = ProcessStep.objects.none()

        
        # Логика фильтрации шагов в выпадающем списке
        if process_id:
            # Если создаем новую уязвимость для конкретного процесса
            self.fields['step'].queryset = ProcessStep.objects.filter(business_process_id=process_id)
        elif self.instance.pk and self.instance.business_process:
            # Если редактируем существующую
            self.fields['step'].queryset = self.instance.business_process.steps.all()
        else:
            # Если контекст неизвестен, список пуст (или можно показать все, но лучше так)
            self.fields['step'].queryset = ProcessStep.objects.none()




class VulnerabilityStatusForm(forms.ModelForm):
    """Быстрое изменение статуса уязвимости"""
    class Meta:
        model = Vulnerability
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class RecommendationForm(forms.ModelForm):
    """Форма для рекомендации"""
    class Meta:
        model = Recommendation
        fields = ['title', 'content', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
        }


class ProcessStepForm(forms.ModelForm):
    """Форма для шагов процесса"""
    class Meta:
        model = ProcessStep
        fields = ['name', 'description', 'order', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название шага'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Описание'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
            'color': forms.Select(attrs={'class': 'form-select'}),
        }
