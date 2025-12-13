from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('processes/', views.business_process_list, name='process_list'),
    path('processes/<int:pk>/', views.business_process_detail, name='process_detail'),
    path('vulnerabilities/', views.vulnerability_list, name='vulnerability_list'),
    path('vulnerabilities/<int:pk>/', views.vulnerability_detail, name='vulnerability_detail'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('profile/', views.profile_view, name='profile'),
]

