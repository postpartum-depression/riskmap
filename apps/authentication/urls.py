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

    # === ВОССТАНОВЛЕНИЕ ПАРОЛЯ ===
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='authentication/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',  # <-- ДОБАВИТЬ
             success_url=reverse_lazy('authentication:password_reset_done')
         ),
         name='password_reset'),

    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='authentication/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='authentication/password_reset_confirm.html',
             success_url=reverse_lazy('authentication:password_reset_complete')  # <-- ДОБАВИТЬ
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='authentication/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]