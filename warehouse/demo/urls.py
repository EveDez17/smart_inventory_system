from django.urls import path
from . import views

app_name = "demo"

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
    # Add other URL patterns for the demo app here
]
