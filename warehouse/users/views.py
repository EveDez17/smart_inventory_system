from django.dispatch import Signal
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import redirect, render, get_object_or_404
from warehouse import settings
from warehouse.users.models import Employee, User
from .forms import EmployeeRegistrationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.views.generic.edit import FormView
from django.utils.crypto import get_random_string
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.views.generic import TemplateView
from django.utils.encoding import force_bytes
import qrcode
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from io import BytesIO
from django.core.mail import send_mail
import logging



logger = logging.getLogger(__name__)

# Check Errors
def csrf_failure(request, reason=""):
    context = {'reason': reason}
    return render(request, "errors/csrf_failure.html", context)

#Base Page
class HomePageView(TemplateView):
    template_name = 'index.html'

#Login Page
def login_view(request):
    if request.method == 'POST':
        # Get username and password from the POST request.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Attempt to authenticate the user.
        user = authenticate(username=username, password=password)

        # If the user is authenticated and active.
        if user is not None and user.is_active:
            login(request, user)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                redirect_url = reverse('dashboard_global:dashboard')  

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if user is not None and user.is_active:
            login(request, user)
            if is_ajax:
                return JsonResponse({'success': True, 'redirect_url': redirect_url})
            else:
                return redirect(redirect_url)

        error_message = 'Invalid username or password.' if user is None else 'Your account is disabled.'
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_message}, status=400)
        else:
            return render(request, 'login.html', {'error': error_message})

    return render(request, 'login.html')

    
#QRcode Login 
def login_with_qr(request, login_token):
    # Replace this with your actual logic for token verification and user authentication
    user = authenticate(login_token=login_token)

    if user is not None:
        # Log the user in
        login(request, user)
        # Redirect to the dashboard
        return redirect(reverse('dashboard'))  # Replace 'dashboard' with the name of your dashboard URL pattern
    else:
        # Handle invalid login token (e.g., show an error page)
        return redirect('invalid_login')  
    
#QRcode Function
def generate_qr(request):
    # Generate a unique token for the user session (replace with your actual logic)
    login_token = "some_unique_token_generated_per_user_session"

    # Generate the login URL with the token
    login_url = request.build_absolute_uri(f'/login-with-qr/{login_token}/')

    # Create a QR code with the login URL
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(login_url)
    qr.make(fit=True)

    # Generate the QR code image
    img = qr.make_image(fill='black', back_color='white')

    # Convert the image to bytes
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    # Return the QR code image as a response
    img_response = HttpResponse(content_type="image/png")
    img.save(img_response, "PNG")
    return img_response
    
#Register Page
def register(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            # Save the form data without committing to the database
            employee = form.save(commit=False)

            # Get the email from the form's cleaned data
            email = form.cleaned_data['email']

            # Create a new User instance and associate it with the Employee
            user = User.objects.create_user(
                username=email.split('@')[0],  # Derive username from email
                email=email,
                password=User.objects.make_random_password()
            )
            employee.user = user

            # Save both Employee and User instances
            employee.save()
            user.save()

            # Confirm the redirection URL is correctly configured in urls.py
            return redirect('users:pending_approval')
        else:
            # Check what errors are present if the form is not valid
            print(form.errors)  # Adding logging to see the errors might help
            return render(request, 'register.html', {'form': form})
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'register.html', {'form': form})





@login_required
@permission_required('users.can_approve_employee', raise_exception=True)
def approve_user(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Check if the employee already has a user account linked
    if employee.user:
        messages.error(request, 'This employee already has a linked user account.')
        return render(request, 'registration/registration_error.html', {'message': 'This employee already has a linked user account.'})
    
    try:
        # Extract username from the employee's email
        username = employee.email.split('@')[0] if employee.email else None
        if not username:
            messages.error(request, 'Invalid email address.')
            return render(request, 'registration/registration_error.html', {'message': 'Invalid email address provided.'})
        
        # Create a new user for the employee
        user = User.objects.create_user(
            username=username,
            email=employee.email,
            password=User.objects.make_random_password()
        )
        employee.user = user
        employee.user.is_approved = True
        employee.user.is_active = True
        employee.user.save()
        employee.save()

        # Sending the approval email
        send_mail(
            'Your Account Has Been Approved',
            f'Here are your login credentials. Username: {user.username}. Please reset your password upon first login.',
            'from@example.com',
            [user.email],
            fail_silently=False,
        )
        messages.success(request, f'Employee {user.username} has been successfully approved and notified.')
        return redirect('users:user_list')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return render(request, 'registration/registration_error.html', {'message': str(e)})

def user_password_reset(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            return redirect('users:password_reset_done')
        else:
            return render(request, 'registration/password_reset.html', {'form': form})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_reset.html', {'form': form})

import logging
logger = logging.getLogger(__name__)

# Pending Approval
@login_required
@permission_required('users.can_view_pending', raise_exception=True)
def pending_approval(request):
    employees_pending = Employee.objects.filter(user__is_approved=False)
    return render(request, 'registration/pending_approval.html', {'employees': employees_pending})

# User credentials deny

@login_required
@permission_required('users.can_modify_user', raise_exception=True)
def deny_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_active = False  # Set the user as inactive or any other status
    user.save()

    messages.info(request, f"User {user.username} has been denied access.")
    return redirect('users:users_dashboard')
# Define the signal
approve_user_signal = Signal()

# User credentials display after approve
@login_required
@permission_required('auth.can_approve_user', raise_exception=True)
def approve_user(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        # Approve the user (example logic)
        user.is_approved = True
        user.save()
        # Generate a new password for the user
        new_password = get_random_string(length=10)  # Generate a random string of length 10
        user.set_password(new_password)
        user.save()
        # Display success message and new user credentials
        full_name = f"{user.first_name} {user.last_name}"
        messages.success(request, f"User '{full_name}' has been successfully approved.")
        context = {
            'username': user.username,
            'password': new_password,
            'email': user.email,
        }
        return render(request, 'registration/new_user_credentials.html', context)
    except User.DoesNotExist:
        # User with the given ID does not exist
        messages.error(request, "User not found.")
        return redirect('users:users_dashboard')
    
# ResetPasword for new User
class CustomPasswordResetView(FormView):
    template_name = 'registration/new_user_password_reset.html'
    success_url = reverse_lazy('users:new_user_password_reset_done')
    form_class = PasswordResetForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        user_model = get_user_model()
        active_users = user_model._default_manager.filter(email__iexact=email, is_active=True)

        for user in active_users:
            subject = "Password Reset Requested"
            email_template_name = "registration/password_reset_email.html"
            context = {
                "email": user.email,
                "domain": settings.SITE_DOMAIN,
                "site_name": "Website",
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": default_token_generator.make_token(user),
                "protocol": settings.EMAIL_PROTOCOL,
            }
            email_body = render_to_string(email_template_name, context)
            msg = EmailMultiAlternatives(subject, email_body, 'no-reply@yourdomain.com', [user.email])
            try:
                msg.send()
            except Exception as e:
                logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
                # Consider adding user feedback here

        return super().form_valid(form)

    
# Email sent with the link to login and change password   
@require_POST  # Ensure that this view only accepts POST requests
def send_password_reset_email(request):
    user_id = request.POST.get('user_id')
    user = get_object_or_404(User, pk=user_id)
    # Construct your email message and send it
    send_mail(
        'Password Reset',
        'Here is your password reset link.',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )
    return HttpResponse('Email sent successfully.')

class PasswordResetDoneView(TemplateView):
    template_name = 'registration/new_user_password_done.html'
    

def custom_logout(request):
    logout(request)
    # Redirect to a success page.
    return redirect('users/logout') 

 

#Dashboard Page
def users_dashboard(request):
    users_to_approve = User.objects.filter(is_approved=False)  # or any other condition
    return render(request, 'dashboard/users_dashboard.html', {'users_to_approve': users_to_approve})

class UsersDashboardView(TemplateView):
    template_name = 'users_dashboard.html'
    context_object_name = 'users_to_approve'
    
    def get_queryset(self):
        # Filter users based on some criteria, e.g., users who are not yet approved
        return User.objects.filter(is_approved=False)  

