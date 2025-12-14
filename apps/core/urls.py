from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('vulnerabilities/create/', views.vulnerability_create, name='vulnerability_create'),

    
    # Процессы
    path('processes/', views.business_process_list, name='process_list'),
    path('processes/create/', views.business_process_create, name='process_create'),
    path('processes/<int:pk>/', views.business_process_detail, name='process_detail'),
    path('processes/<int:pk>/edit/', views.business_process_edit, name='process_edit'),
    path('processes/<int:pk>/delete/', views.business_process_delete, name='process_delete'),
    path('import/', views.import_processes, name='import_processes'),
    
    # Уязвимости
    path('vulnerabilities/', views.vulnerability_list, name='vulnerability_list'),
    path('vulnerabilities/<int:pk>/', views.vulnerability_detail, name='vulnerability_detail'),
    
    # Рекомендации
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('vulnerabilities/<int:vulnerability_pk>/recommendation/add/', views.add_recommendation, name='add_recommendation'),
    
    # Профиль
    path('profile/', views.profile_view, name='profile'),
]
