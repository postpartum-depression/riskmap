from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя"""
    email = models.EmailField(unique=True, verbose_name='Email')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']
        db_table = 'users'
    
    def __str__(self):
        return self.username
