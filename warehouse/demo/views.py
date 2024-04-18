from django.http import HttpResponse
from django.shortcuts import redirect, render
from warehouse.demo.admin import CustomUserCreationForm
from warehouse.demo.forms import EmployeeRegistrationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, permission_required
import qrcode
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from io import BytesIO
from django.middleware.csrf import get_token
from django.contrib import messages
from django.middleware.csrf import get_token
import logging

from warehouse.inventory.models import User

logger = logging.getLogger(__name__)

# Check Errors
def csrf_failure(request, reason=""):
    context = {'reason': reason}
    return render(request, "errors/csrf_failure.html", context)
#Base Page
def home(request):
    return render(request, "base.html")

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
                return redirect('demo:dashboard')  # Ensure 'demo:dashboard' is correctly defined in urls.py
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
                return JsonResponse({'success': True, 'redirect_url': '/dashboard/'})
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
        return redirect('demo:dashboard')  # Replace 'dashboard' with the name of your dashboard URL pattern
    else:
        # Handle invalid login token (e.g., show an error page)
        return redirect('invalid_login')  
    
#Register Page
def register(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)
        employee_form = EmployeeRegistrationForm(request.POST)
        
        # Check if 'terms' checkbox is checked
        if 'terms' not in request.POST:
            messages.error(request, "You must agree to the terms to register.")
        elif user_form.is_valid() and employee_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False  # User will not be active until approved
            user.save()
            
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            
            # Optionally send an email here for account verification or admin approval
            
            messages.success(request, "Your account has been created and is pending approval.")
            return redirect('account_pending_approval')  # Redirect to a pending approval page
        else:
            # If the forms have errors, these will be passed to the template and displayed
            messages.error(request, "Please correct the errors below.")
        
        # Render the same page with the form data filled in and errors shown
        return render(request, 'registration/register.html', {
            'user_form': user_form,
            'employee_form': employee_form
        })

    else:
        user_form = CustomUserCreationForm()
        employee_form = EmployeeRegistrationForm()

    return render(request, 'registration/register.html', {
        'user_form': user_form,
        'employee_form': employee_form
    })

def pending_approval(request):
    return render(request, 'registration/pending_approval.html')

@login_required
@permission_required('is_superuser')
def approve_user(request, user_id):
    user = User.objects.get(id=user_id)
    user.is_approved = True
    user.save()
    # Redirect to the user list page or wherever is appropriate
    return redirect('user_list')


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

#Dashboard Page
def dashboard(request):
    # You can fetch data or perform any other logic here before rendering the template
    return render(request, 'dashboard.html')


