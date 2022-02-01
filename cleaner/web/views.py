from django.shortcuts import render
from .forms import UserLoginForm
from django.contrib.auth import authenticate, login, logout


# Create your views here.
def index(request):
    context = {}
    return render(request, 'index.html', context)


def login_(request):
    # login form
    log_in = UserLoginForm(request.POST or None)
    if log_in.is_valid():
        username = log_in.cleaned_data.get('username')
        password = log_in.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
    context = {
        'log_in': log_in,
    }
    return render(request, 'login.html', context)
