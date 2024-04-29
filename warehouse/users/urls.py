from django.urls import path
from warehouse.users import views


app_name = "users"

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('users_dashboard/', views.UsersDashboardView.as_view(), name='users_dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),
    path('deny_user/<int:user_id>/', views.deny_user, name='deny_user'),
    path('approve_user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('new-user/password-reset/', views.CustomPasswordResetView.as_view(), name='new_user_password_reset'),
    path('new-user/password-reset/done/', views.PasswordResetDoneView.as_view(), name='new_user_password_reset_done'),
    path('send_password_reset_email/', views.send_password_reset_email, name='send_password_reset_email'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
    # Add other URL patterns for the demo app here
    # Make sure you add the QR login URL
    path('login-with-qr/<login_token>/', views.login_with_qr, name='login_with_qr'),
]

