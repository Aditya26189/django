from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.shortcuts import redirect, render, get_object_or_404
from .models import CustomUser
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from .forms import UserUpdateForm
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.utils.safestring import mark_safe

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
# from django.contrib.auth.models import User

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been activated successfully.')
        return redirect('/')
    else:
        messages.error(request, 'The activation link is invalid or expired.')
        return redirect('/')


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("email/verification_email.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, mark_safe(
            f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on the '
            'received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.'
        ))
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')
        


  

            
# @user_not_authenticated
def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  
            user.save()
            user.send_verification_email()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('/login')  

    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})



def send_verification_email(user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = f"{settings.SITE_URL}/verify/{uid}/{token}/"
    
    subject = 'Verify your email address'
    html_content = render_to_string('email/verification_email.html', {
        'user': user,
        'verification_link': verification_link,
    })
    text_content = f"Welcome, {user.username}!\nThank you for registering with us. Please click the link below to verify your email address:\n{verification_link}\nIf you did not register, please ignore this email."
    
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, "text/html")
    email.send()

def verify(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been verified. You can now log in.')
        return redirect('/login')
    else:
        messages.error(request, 'The verification link is invalid.')
        return redirect('/')
    

# from django.contrib.auth import authenticate, login, logout
# from django.shortcuts import render, redirect
# from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'users/login.html')

@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users/login.html')


@login_required
def profile(request):
    return render(request, 'users/dashboard.html')



@login_required
def dashboard(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:dashboard')
    else:
        form = UserUpdateForm(instance=request.user)

    all_users = CustomUser.objects.all()

    return render(request, 'users/dashboard.html', {
        'form': form,
        'all_users': all_users
    })