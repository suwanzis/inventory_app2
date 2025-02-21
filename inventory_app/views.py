from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from .forms import CustomUserCreationForm
from .models import Product




def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inventory_list')
        else:
            error_message = '用户名或密码错误'
            return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def inventory_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    products = Product.objects.filter(user=request.user)
    return render(request, 'inventory_list.html', {'products': products})