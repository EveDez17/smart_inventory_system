from django.http import HttpResponse
from django.shortcuts import redirect, render
from warehouse.demo.forms import EmployeeRegistrationForm
from django.contrib.auth import authenticate, login
from warehouse.inventory.models import User
import qrcode
from io import BytesIO

def home(request):
    return render(request, "base.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('home')  # Replace 'home' with the name of the route you want to redirect to
        else:
            # Return an 'invalid login' error message.
            return render(request, 'login.html', {'error': 'Invalid username or password.'})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        form = EmployeeRegistrationForm(request.POST)
        if form.is_valid():
            # Assuming the form includes a field for selecting the role ID
            role_id = form.cleaned_data['role']  
            role = User.Role.objects.get(id=role_id)  # Access the Role choices directly from the User model
            
            # Create a new user account
            user = form.save(commit=False)
            user.role = role  # Assign the selected role to the user
            user.save()

            # Redirect to a success page or login page
            return redirect('login')  # Replace 'login' with the actual URL name for your login page
    else:
        form = EmployeeRegistrationForm()
    
    return render(request, 'register.html', {'form': form})



def generate_qr(request):
    # Replace with your actual logic for generating a unique identifier/token
    login_token = "some_unique_token_generated_per_user_session"

    # This could be a URL to an endpoint that handles the token
    login_url = request.build_absolute_uri(f'/login-with-qr/{login_token}/')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(login_url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)

    return HttpResponse(buffer, content_type='image/png')
