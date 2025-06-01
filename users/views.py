from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

# Create your views here.
def login_views(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_staff:
                login(request, user)
                return redirect('main-page')
            else:
                messages.error(request, 'Access denied. Staff only')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def main_page(request):
    return render(request, 'users/main.html')

class CustomLoginView(LoginView):
    template_name = 'users/login.html'