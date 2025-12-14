from django import forms
from .models import BusinessProcess, Vulnerability, Recommendation, AuditLog

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
        fields = ['title', 'description', 'business_process', 'severity', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            # Важно: добавляем класс form-select для красивого выпадающего списка
            'business_process': forms.Select(attrs={'class': 'form-select'}), 
            'severity': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    # Добавляем этот метод, чтобы убедиться, что список загружается
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Если вдруг процессов нет, поле будет пустым, но видимым
        self.fields['business_process'].queryset = BusinessProcess.objects.all()
        self.fields['business_process'].empty_label = "Выберите процесс..."


class VulnerabilityStatusForm(forms.ModelForm):
    """Быстрое изменение статуса уязвимости"""
    class Meta:
        model = Vulnerability
        fields = ['status']  # assigned_to убрали
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
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
