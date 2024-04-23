from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.dispatch import receiver
from .signals import user_approved

@receiver(user_approved)
def send_approval_email(sender, user, request, **kwargs):
    # Generate a password reset token
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_url = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

    subject = "Your Account Has Been Approved"
    message = f"Please set your password by following this link: {reset_url}"
    from_email = 'from@example.com'  # Replace with your actual sender email
    recipient_list = [user.email]

    send_mail(subject, message, from_email, recipient_list)
