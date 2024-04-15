from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = "demo"

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Add other URL patterns for the demo app here
]
