from django.urls import path
from . import views
from .views import pending_approval, register


app_name = "demo"

urlpatterns = [
    path('home/', views.home, name="home"),
    path('login/', views.login_view, name='login'),
    path('register/', register, name='register'),
    path('pending_approval/', pending_approval, name='pending_approval'),
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Add other URL patterns for the demo app here
]
