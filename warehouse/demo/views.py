from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from warehouse.demo.admin import CustomUserCreationForm
from warehouse.demo.forms import EmployeeRegistrationForm, UserRegistrationForm
from django.contrib.auth import authenticate, login
import qrcode
from django.http import JsonResponse
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.middleware.csrf import get_token
import logging
from django.middleware.csrf import get_token
import logging

logger = logging.getLogger(__name__)

# Check Errors
def csrf_failure(request, reason=""):
    context = {'reason': reason}
    return render(request, "errors/csrf_failure.html", context)
#Base Page
def home(request):
    return render(request, "base.html")

#Login Page
def login_view(request):
    if request.method == 'POST':
        # Log the received CSRF token
        received_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
        logger.info(f"Received CSRF token: {received_csrf_token}")

        # Get the CSRF token expected by Django
        expected_csrf_token = get_token(request)
        logger.info(f"Expected CSRF token: {expected_csrf_token}")

        email = request.POST.get('username')  # Assuming this field is actually for the email
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)  # Authenticate with email
        if user is not None:
            login(request, user)
            return redirect('demo:dashboard')  # Redirect to the dashboard URL pattern name
        else:
            # Return an error message to the login template
            return render(request, 'login.html', {'error': 'Invalid email or password.'})
    else:
        # Display the login page if not a POST request
        return render(request, 'login.html')
#Cookie for Login    
def ajax_login_view(request):
    if request.method == 'POST' and request.is_ajax():
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)  # Use email to authenticate
        if user is not None:
            login(request, user)
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})
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
        
        if user_form.is_valid() and employee_form.is_valid():
            user = user_form.save()
            # If you want the user to verify their email or be approved by an admin, do not log them in immediately
            # login(request, user)  # Log the user in

            # Link the employee profile to the newly created user
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()
            
            # Redirect to a page where you inform the user that their account is pending approval
            return redirect('account_pending_approval')
        else:
            # If there are form errors, add them to the context
            context = {
                'user_form': user_form,
                'employee_form': employee_form
            }
            if not user_form.is_valid():
                context['user_errors'] = user_form.errors
            if not employee_form.is_valid():
                context['employee_errors'] = employee_form.errors
            return render(request, 'registration/register.html', context)
    else:
        user_form = CustomUserCreationForm()
        employee_form = EmployeeRegistrationForm()

    return render(request, 'registration/register.html', {
        'user_form': user_form,
        'employee_form': employee_form
    })

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


