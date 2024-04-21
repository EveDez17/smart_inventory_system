from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required, login_required
from django.shortcuts import redirect, render, get_object_or_404
from warehouse.users.models import Employee, User
from .forms import EmployeeRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import login, update_session_auth_hash
import qrcode
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from io import BytesIO
from django.middleware.csrf import get_token
from django.core.mail import send_mail
from django.middleware.csrf import get_token
import logging



logger = logging.getLogger(__name__)

# Check Errors
def csrf_failure(request, reason=""):
    context = {'reason': reason}
    return render(request, "errors/csrf_failure.html", context)
#Base Page
def home(request):
    return render(request, "home.html")

#Login Page
logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        # Log the received CSRF token
        received_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
        logger.info(f"Received CSRF token: {received_csrf_token}")

        # Get the CSRF token expected by Django
        expected_csrf_token = get_token(request)
        logger.info(f"Expected CSRF token: {expected_csrf_token}")

        email = request.POST.get('username')  # Assuming the username field is used for the email
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)  # Use authenticate correctly

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('users:dashboard'))  # Ensure 'demo:dashboard' is correctly defined in urls.py
            else:
                return render(request, 'login.html', {'error': 'Your account is disabled.'})
        else:
            # Return an error message to the login template
            return render(request, 'login.html', {'error': 'Invalid email or password.'})
    else:
        # Display the login page if not a POST request
        return render(request, 'login.html')
#Cookie for Login    
@require_POST
@csrf_exempt  # Generally avoid using csrf_exempt; it's shown here for illustrative purposes
def ajax_login_view(request):
    if request.is_ajax():
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                logger.info(f"User {username} logged in via AJAX.")
                return JsonResponse({'success': True, 'redirect_url': reverse('demo:dashboard')})
            else:
                logger.warning(f"Disabled account login attempt via AJAX: {username}")
                return JsonResponse({'success': False, 'error': 'Your account is disabled.'})
        else:
            logger.warning(f"Failed AJAX login attempt for username: {username}")
            return JsonResponse({'success': False, 'error': 'Invalid username or password.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)
    
#QRcode Login 
def login_with_qr(request, login_token):
    # Replace this with your actual logic for token verification and user authentication
    user = authenticate(login_token=login_token)

    if user is not None:
        # Log the user in
        login(request, user)
        # Redirect to the dashboard
        return redirect(reverse('users:dashboard'))  # Replace 'dashboard' with the name of your dashboard URL pattern
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

            return redirect('users:pending_approval')
        else:
            return render(request, 'registration/register.html', {'form': form})
    else:
        form = EmployeeRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
@permission_required('users.can_approve_employee', raise_exception=True)
def approve_user(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    if employee.user:
        messages.error(request, 'This employee already has a linked user account.')
        return render(request, 'registration/registration_error.html', {'message': 'This employee already has a linked user account.'})
    
    try:
        # Create a user for the employee if it does not exist
        username = employee.email.split('@')[0] if employee.email else None
        if not username:
            messages.error(request, 'Invalid email address.')
            return render(request, 'registration/registration_error.html', {'message': 'Invalid email address provided.'})
        
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

        send_mail(
            'Your Account Has Been Approved',
            f'Here are your login credentials. Username: {user.username} Please reset your password upon first login.',
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
            return redirect('password_reset_done')
        else:
            return render(request, 'registration/password_reset.html', {'form': form})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_reset.html', {'form': form})

@login_required
@permission_required('users.can_view_pending', raise_exception=True)
def pending_approval(request):
    employees_pending = Employee.objects.filter(user__is_approved=False)
    return render(request, 'registration/pending_approval.html', {'employees': employees_pending})





#Dashboard Page
def dashboard(request):
    # You can fetch data or perform any other logic here before rendering the template
    return render(request, 'dashboard.html')

