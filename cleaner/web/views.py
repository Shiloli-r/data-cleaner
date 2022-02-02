from django.shortcuts import render, redirect
from .forms import UserLoginForm, CreateUser, FileForm
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import File


# Create your views here.
def index(request):
    form = FileForm(request.POST, request.FILES)
    if form.is_valid():
        upload = request.FILES.get('file')
        file_ = File.objects.create(upload=upload)
        file_.save()
    context = {
        'form': form,
    }
    return render(request, 'index.html', context)


def login_(request):
    # login form
    log_in = UserLoginForm(request.POST or None)
    if log_in.is_valid():
        username = log_in.cleaned_data.get('username')
        password = log_in.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('/')
    context = {
        'log_in': log_in,
    }
    return render(request, 'login.html', context)


def sign_up(request):
    sign_up_ = CreateUser(request.POST or None)
    if sign_up_.is_valid():
        username = sign_up_.cleaned_data.get('username')
        password = sign_up_.cleaned_data.get('password')
        sign_up_.save()
        authenticate(username=username, password=password)
        user = User.objects.get(username=username)
        login(request, user)
        return redirect('/')
    context = {
        "sign_up": sign_up_,
    }
    return render(request, 'signup.html', context)


@login_required
def logout(request):
    django_logout(request)
    return redirect('/')
