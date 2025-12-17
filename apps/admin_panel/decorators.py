from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """Декоратор для проверки прав администратора"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Необходима авторизация')
            return redirect('authentication:login')
        
        # Проверяем стандартный флаг суперпользователя
        if not request.user.is_superuser:
            messages.error(request, 'Доступ запрещен. Требуются права администратора.')
            return redirect('core:dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper
