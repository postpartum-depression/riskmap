from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('vulnerabilities/', views.vulnerability_management, name='vulnerability_management'),
    path('processes/', views.process_management, name='process_management'),
]
