from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from .decorators import admin_required

User = get_user_model()

@admin_required
def admin_dashboard(request):
    """Главная страница админ-панели"""
    # Пока просто перенаправляем на управление пользователями
    return redirect('admin_panel:user_management')

@admin_required
def user_management(request):
    """Список всех пользователей"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/user_management.html', {'users': users})

@admin_required
def delete_user(request, user_id):
    """Удаление пользователя"""
    if request.method == 'POST':
        # Защита: нельзя удалить самого себя
        if request.user.id == user_id:
            messages.error(request, "Нельзя удалить собственного пользователя!")
            return redirect('admin_panel:user_management')
            
        user = get_object_or_404(User, id=user_id)
        username = user.username
        user.delete()
        messages.success(request, f"Пользователь {username} был успешно удален.")
        
    return redirect('admin_panel:user_management')

def vulnerability_management(request):
    return render(request, 'admin_panel/dashboard.html', {'title': 'Уязвимости (в разработке)'})

def process_management(request):
    return render(request, 'admin_panel/dashboard.html', {'title': 'Процессы (в разработке)'})
