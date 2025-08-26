from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from .forms import UserRegisterForm


def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.role != 'admin':
                user.is_staff = False
                user.is_superuser = False
            user.save()
            messages.success(request, 'Account created. Please login.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # 1. Empty checks
        if not username and not password:
            messages.error(request, "Username and password are required.", extra_tags="login_error")
            return render(request, 'accounts/login.html')
        elif not username:
            messages.error(request, "Username is required.", extra_tags="username_error")
            return render(request, 'accounts/login.html')
        elif not password:
            messages.error(request, "Password is required.", extra_tags="password_error")
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=username, password=password)

        if user:
            request.session['user_id'] = user.id
            request.session['role'] = user.role

            messages.success(request, f"Welcome, {user.get_full_name() or user.username}!")

            if user.role == 'doctor':
                return redirect('doctor:dashboard')
            elif user.role == 'admin':
                return redirect('adminpanel:admin_dashboard')
            else:
                return redirect('patient:patient_dashboard')
        else:
            messages.error(request, "Invalid username or password.", extra_tags="login_error")

    return render(request, 'accounts/login.html')


def logout_view(request):
    request.session.flush()
    messages.info(request, 'You are logged out.')
    return redirect('accounts:login')
