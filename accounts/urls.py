from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_user, name='login-user'),
    path('register/', views.register_user, name='register-user'),
]
