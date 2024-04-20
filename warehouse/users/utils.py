from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.conf import settings

def send_admin_approval_request(user):
    User = get_user_model()  # Move inside the function to avoid the error
    subject = 'New User Approval Needed'
    message = f'Please review and approve the new user: {user.email}, Role: {user.get_role_display()}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [admin.email for admin in User.objects.filter(is_superuser=True)]
    send_mail(subject, message, from_email, recipient_list)
