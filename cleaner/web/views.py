from django.shortcuts import render, redirect
from .forms import UserLoginForm, CreateUser, FileForm
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from uuid import uuid4
import pandas as pd
import numpy as np
import os

from .models import File


# Create your views here.
def index(request):
    form = FileForm(request.POST, request.FILES)
    if form.is_valid():
        upload = request.FILES.get('file')
        file = File.objects.create(upload=upload)
        file.save()
        return redirect('/clean')
    if request.method == 'POST':
        files = request.FILES.getlist('datafiles')
        parent = "../cleaner/media"
        path = os.path.join(parent, "input")
        try:
            os.mkdir(path)
        except FileExistsError:
            import shutil
            shutil.rmtree(path)
            os.mkdir(path)
        for file in files:
            with open(path+"/{}.jpg".format(uuid4()), 'wb+') as f:
                for chunk in file.chunks():
                    f.write(chunk)
            return redirect('/clean-images')
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


def clean_images(request):
    parent_dir = "../cleaner/media"
    path = os.path.join(parent_dir, "input")
    context = {

    }
    return render(request, "clean-images.html", context)


def clean(request):
    file = File.objects.latest('id')
    missing_values = ["N/a", "na", np.nan]
    try:
        df = pd.read_csv(file.upload.path, na_values=missing_values)
    except UnicodeDecodeError:
        df = pd.read_excel(file.upload.path, na_values=missing_values)
    rows = []

    # check for any cleaning operations underway
    drop_m_ = request.GET.get('drop_m')
    drop_d_ = request.GET.get('drop_d')
    ffill_ = request.GET.get('ffill')
    bfill_ = request.GET.get('bfill')
    interpolate_ = request.GET.get('interpolate')
    if drop_m_:
        df = drop_m(df)
        df.to_csv(file.upload.path, index=False)
        return redirect('/clean')
    if drop_d_:
        df = drop_d(df)
        df.to_csv(file.upload.path, index=False)
        return redirect('/clean')
    if ffill_:
        df = f_fill(df)
        df.to_csv(file.upload.path, index=False)
        return redirect('/clean')
    if bfill_:
        df = b_fill(df)
        df.to_csv(file.upload.path, index=False)
        return redirect('/clean')
    if interpolate_:
        try:
            df = interpolate_(df)
        except TypeError:
            pass
        df.to_csv(file.upload.path, index=False)
        return redirect('/clean')
    # Create the rows of the table
    for i in range(df.shape[0]):  # rows
        rows.append([])
        for j in range(df.shape[1]):  # columns
            rows[i].append(df.iloc[i][j])
    context = {
        'columns': df.columns,
        'rows': rows,
        'download': file.upload.url,
    }
    return render(request, 'clean.html', context)


def drop_m(dataframe):
    dataframe = dataframe.dropna()
    return dataframe


def drop_d(dataframe):
    df = dataframe.drop_duplicates(keep='first')
    return df


def f_fill(dataframe):
    dataframe = dataframe.fillna(method="ffill")
    return dataframe


def b_fill(dataframe):
    dataframe = dataframe.fillna(method="bfill")
    return dataframe


def interpolate(dataframe):
    dataframe = dataframe.interpolate()
    return dataframe
