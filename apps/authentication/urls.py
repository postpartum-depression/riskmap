from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

app_name = 'authentication'  

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='authentication/password_change.html',
             success_url=reverse_lazy('authentication:password_change_done') 
         ), 
         name='password_change'),

    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='authentication/password_change_done.html'
         ), 
         name='password_change_done'),
]


