from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count


from .models import BusinessProcess, Vulnerability, Recommendation, AuditLog
from .forms import (
    BusinessProcessForm, VulnerabilityForm,
    VulnerabilityStatusForm, RecommendationForm
)
from .services import import_processes_from_file


def home_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    return render(request, 'core/home.html')



@login_required
def dashboard_view(request):
    """Главный дашборд с аналитикой"""
    processes = BusinessProcess.objects.filter(owner=request.user)
    vulnerabilities = Vulnerability.objects.filter(business_process__owner=request.user)
    
    stats = {
        'total': vulnerabilities.count(),
        'high': vulnerabilities.filter(severity__gte=4).count(),
        'medium': vulnerabilities.filter(severity=3).count(),
        'resolved': vulnerabilities.filter(status='resolved').count(),
    }

    status_counts = vulnerabilities.values('status').annotate(count=Count('id'))
    status_dict = {item['status']: item['count'] for item in status_counts}
    
    sorted_processes = sorted(processes, key=lambda p: p.risk_score, reverse=True)[:5]
    risk_chart_labels = [p.name for p in sorted_processes]
    risk_chart_data = [p.risk_score for p in sorted_processes]

    context = {
        'stats': stats,
        'processes_count': processes.count(),
        'recent_processes': processes[:5],
        'risk_chart_labels': risk_chart_labels,
        'risk_chart_data': risk_chart_data,
        'status_chart_open': status_dict.get('open', 0),
        'status_chart_in_progress': status_dict.get('in_progress', 0),
        'status_chart_resolved': status_dict.get('resolved', 0),
        'status_chart_closed': status_dict.get('closed', 0),
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def import_processes(request):
    """Импорт процессов из файла"""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid() and request.FILES:
            file = request.FILES['file']
            count_created, count_skipped, errors = import_processes_from_file(file, request.user)
            
            if count_created > 0:
                messages.success(request, f"✅ Успешно импортировано: {count_created} процессов")
            
            if errors:
                for error in errors[:5]:
                    messages.warning(request, error)
            
            return redirect('core:process_list')
    else:
        form = UploadFileForm()
    
    return render(request, 'core/import.html', {'form': form})


@login_required
def business_process_list(request):
    """Список всех процессов пользователя"""
    processes = BusinessProcess.objects.filter(owner=request.user)
    
    show_inactive = request.GET.get('show_inactive') == 'true'
    if not show_inactive:
        processes = processes.filter(is_active=True)
    
    context = {
        'processes': processes,
        'show_inactive': show_inactive,
    }
    return render(request, 'core/business_process_list.html', context)


@login_required
def business_process_create(request):
    """Создание нового процесса"""
    if request.method == 'POST':
        form = BusinessProcessForm(request.POST)
        if form.is_valid():
            process = form.save(commit=False)
            process.owner = request.user
            process.save()
            messages.success(request, f"✅ Процесс '{process.name}' успешно создан!")
            return redirect('core:process_detail', pk=process.pk)
    else:
        form = BusinessProcessForm()
    
    context = {'form': form, 'title': 'Создать новый процесс'}
    return render(request, 'core/business_process_form.html', context)


@login_required
def business_process_detail(request, pk):
    """Детали процесса с его уязвимостями"""
    process = get_object_or_404(BusinessProcess, pk=pk, owner=request.user)
    vulnerabilities = process.vulnerabilities.all()
    
    stats = {
        'total': vulnerabilities.count(),
        'critical': vulnerabilities.filter(severity=5).count(),
        'high': vulnerabilities.filter(severity=4).count(),
        'open': vulnerabilities.filter(status='open').count(),
        'resolved': vulnerabilities.filter(status='resolved').count(),
    }

    context = {
        'process': process,
        'vulnerabilities': vulnerabilities,
        'stats': stats,
    }
    return render(request, 'core/business_process_detail.html', context)


@login_required
def business_process_edit(request, pk):
    """Редактирование процесса"""
    process = get_object_or_404(BusinessProcess, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        form = BusinessProcessForm(request.POST, instance=process)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Процесс '{process.name}' обновлен!")
            return redirect('core:process_detail', pk=process.pk)
    else:
        form = BusinessProcessForm(instance=process)
    
    context = {'form': form, 'process': process, 'title': 'Редактировать процесс'}
    return render(request, 'core/business_process_form.html', context)


@login_required
def business_process_delete(request, pk):
    """Удаление процесса"""
    process = get_object_or_404(BusinessProcess, pk=pk, owner=request.user)
    
    if request.method == 'POST':
        process_name = process.name
        process.delete()
        messages.success(request, f"✅ Процесс '{process_name}' удален!")
        return redirect('core:process_list')
    
    context = {'process': process}
    return render(request, 'core/business_process_confirm_delete.html', context)


@login_required
def vulnerability_list(request):
    """Список всех уязвимостей пользователя"""
    vulnerabilities = Vulnerability.objects.filter(
        business_process__owner=request.user
    )
    
    status_filter = request.GET.get('status')
    if status_filter:
        vulnerabilities = vulnerabilities.filter(status=status_filter)
    
    context = {
        'vulnerabilities': vulnerabilities,
        'status_filter': status_filter,
    }
    return render(request, 'core/vulnerability_list.html', context)


@login_required
def vulnerability_detail(request, pk):
    """Детали уязвимости с историей и рекомендациями"""
    vulnerability = get_object_or_404(
        Vulnerability,
        pk=pk,
        business_process__owner=request.user
    )
    recommendations = vulnerability.recommendations.all()
    audit_logs = vulnerability.audit_logs.all()

    if request.method == 'POST':
        form = VulnerabilityStatusForm(request.POST, instance=vulnerability)
        if form.is_valid():
            old_status = vulnerability.status
            old_assigned = vulnerability.assigned_to
            
            vulnerability = form.save()
            
            if old_status != vulnerability.status:
                AuditLog.objects.create(
                    vulnerability=vulnerability,
                    user=request.user,
                    action='status_changed',
                    old_value=old_status,
                    new_value=vulnerability.status
                )
                messages.success(request, f"Статус изменен на '{vulnerability.get_status_display()}'")
            
            if old_assigned != vulnerability.assigned_to:
                AuditLog.objects.create(
                    vulnerability=vulnerability,
                    user=request.user,
                    action='assigned',
                    old_value=str(old_assigned),
                    new_value=str(vulnerability.assigned_to)
                )
                messages.success(request, "Назначение обновлено")
            
            return redirect('core:vulnerability_detail', pk=pk)
    else:
        form = VulnerabilityStatusForm(instance=vulnerability)

    context = {
        'vulnerability': vulnerability,
        'recommendations': recommendations,
        'audit_logs': audit_logs,
        'form': form,
    }
    return render(request, 'core/vulnerability_detail.html', context)


@login_required
def add_recommendation(request, vulnerability_pk):
    """Добавить рекомендацию к уязвимости"""
    vulnerability = get_object_or_404(
        Vulnerability,
        pk=vulnerability_pk,
        business_process__owner=request.user
    )

    if request.method == 'POST':
        form = RecommendationForm(request.POST)
        if form.is_valid():
            recommendation = form.save(commit=False)
            recommendation.vulnerability = vulnerability
            recommendation.save()
            messages.success(request, "Рекомендация добавлена")
            return redirect('core:vulnerability_detail', pk=vulnerability_pk)
    else:
        form = RecommendationForm()

    context = {
        'form': form,
        'vulnerability': vulnerability,
    }
    return render(request, 'core/add_recommendation.html', context)


@login_required
def recommendations_view(request):
    """Список всех рекомендаций"""
    recommendations = Recommendation.objects.filter(
        vulnerability__business_process__owner=request.user
    )
    
    show_implemented = request.GET.get('show_implemented') == 'true'
    if not show_implemented:
        recommendations = recommendations.filter(is_implemented=False)
    
    context = {
        'recommendations': recommendations,
        'show_implemented': show_implemented,
    }
    return render(request, 'core/recommendations.html', context)


@login_required
def profile_view(request):
    """Профиль пользователя"""
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'core/profile.html', context)

@login_required
def vulnerability_create(request):
    if request.method == 'POST':
        form = VulnerabilityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Уязвимость добавлена!')
            return redirect('core:vulnerability_list')
    else:
        form = VulnerabilityForm()
    
    return render(request, 'core/vulnerability_form.html', {'form': form, 'title': 'Новая уязвимость'})
