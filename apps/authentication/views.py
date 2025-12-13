from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import LoginForm, RegisterForm


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('authentication:login')
    else:
        form = RegisterForm()
    
    return render(request, 'authentication/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы вышли из системы')
    return redirect('core:home')
