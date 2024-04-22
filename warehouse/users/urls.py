from django.urls import path
from warehouse.users import views


app_name = "users"

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('pending_approval/', views.pending_approval, name='pending_approval'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Add other URL patterns for the demo app here
]
