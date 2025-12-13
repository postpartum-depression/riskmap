from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import BusinessProcess, Vulnerability, Recommendation


def home_view(request):
    return render(request, 'core/home.html')


@login_required
def dashboard_view(request):
    processes = BusinessProcess.objects.filter(owner=request.user)
    total_vulnerabilities = sum(p.vulnerability_count for p in processes)
    
    context = {
        'processes_count': processes.count(),
        'vulnerabilities_count': total_vulnerabilities,
        'recent_processes': processes[:5],
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def business_process_list(request):
    processes = BusinessProcess.objects.filter(owner=request.user)
    context = {
        'processes': processes,
    }
    return render(request, 'core/business_process_list.html', context)


@login_required
def business_process_detail(request, pk):
    process = get_object_or_404(BusinessProcess, pk=pk, owner=request.user)
    vulnerabilities = process.vulnerabilities.all()
    
    context = {
        'process': process,
        'vulnerabilities': vulnerabilities,
    }
    return render(request, 'core/business_process_detail.html', context)


@login_required
def vulnerability_list(request):
    vulnerabilities = Vulnerability.objects.filter(
        business_process__owner=request.user
    )
    context = {
        'vulnerabilities': vulnerabilities,
    }
    return render(request, 'core/vulnerability_list.html', context)


@login_required
def vulnerability_detail(request, pk):
    vulnerability = get_object_or_404(
        Vulnerability,
        pk=pk,
        business_process__owner=request.user
    )
    recommendations = vulnerability.recommendations.all()
    
    context = {
        'vulnerability': vulnerability,
        'recommendations': recommendations,
    }
    return render(request, 'core/vulnerability_detail.html', context)


@login_required
def recommendations_view(request):
    recommendations = Recommendation.objects.filter(
        vulnerability__business_process__owner=request.user
    )
    context = {
        'recommendations': recommendations,
    }
    return render(request, 'core/recommendations.html', context)

@login_required
def profile_view(request):
    user = request.user  # текущий пользователь
    context = {
        'user': user,
    }
    return render(request, 'core/profile.html', context)
