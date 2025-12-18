from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Главная и дашборд
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Процессы
    path('processes/', views.business_process_list, name='process_list'),
    path('processes/create/', views.business_process_create, name='process_create'),
    path('processes/<int:pk>/', views.business_process_detail, name='process_detail'),
    path('processes/<int:pk>/edit/', views.business_process_edit, name='process_edit'),
    path('processes/<int:pk>/delete/', views.business_process_delete, name='process_delete'),
    
    # Декомпозиция и шаги
    path('processes/<int:pk>/decomposition/', views.process_decomposition, name='process_decomposition'),
    path('processes/<int:pk>/steps/', views.manage_process_steps, name='manage_steps'),

    # Уязвимости (список и детали)
    path('vulnerabilities/', views.vulnerability_list, name='vulnerability_list'),
    path('vulnerabilities/<int:pk>/', views.vulnerability_detail, name='vulnerability_detail'),
    
    # === ВАЖНО: Маршруты для создания/редактирования/удаления уязвимостей ===
    # Обрати внимание: create принимает process_pk!
    path('process/<int:process_pk>/add_vulnerability/', views.vulnerability_create, name='vulnerability_create'),
    path('vulnerability/<int:pk>/edit/', views.vulnerability_edit, name='vulnerability_edit'),
    path('vulnerabilities/<int:pk>/delete/', views.vulnerability_delete, name='vulnerability_delete'),

    # Рекомендации и профиль
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('vulnerabilities/<int:vulnerability_pk>/recommendation/add/', views.add_recommendation, name='add_recommendation'),
    path('profile/', views.profile_view, name='profile'),
     
    # Автоскан
    path('processes/<int:pk>/autoscan/', views.process_auto_scan, name='process_autoscan'),
]