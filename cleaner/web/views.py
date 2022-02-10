from django.shortcuts import render, redirect
from .forms import UserLoginForm, CreateUser, FileForm
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from keras.preprocessing.image import load_img, image_dataset_from_directory
from keras.preprocessing.image import img_to_array
from keras.applications.vgg16 import preprocess_input
from keras.applications.vgg16 import decode_predictions
from keras.applications.vgg16 import VGG16

from uuid import uuid4
import pandas as pd
import numpy as np
import os

from .models import File


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


@run_once
def create_model():
    model = VGG16()
    return model


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
            with open(path + "/{}.jpg".format(uuid4()), 'wb+') as f:
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
    unrecognized = request.GET.get('unrecognized')
    majority = request.GET.get('majority')
    minority = request.GET.get('minority')

    parent_dir = "../cleaner/media"
    path = os.path.join(parent_dir, "input")

    # load the model
    #  model = create_model()
    model = VGG16()

    # load images from directory
    directory_in_str = path
    directory = os.fsencode(directory_in_str)
    img_paths = []
    filenames = []

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        img_paths.append(directory_in_str + "/" + filename)
        filenames.append(filename)

    # Get the breeds
    dog_breeds = []
    with open("../dog_breeds.txt", encoding='utf-8') as f:
        for line in f:
            line = str(line)
            dog_breeds.append(line.replace('\n', ''))

    cat_breeds = []
    with open("../cat_breeds.txt", encoding='utf-8') as f:
        for line in f:
            line = str(line)
            cat_breeds.append(line.replace('\n', ''))

    dogs = []
    cats = []
    misc = []
    predictions = []
    for path in img_paths:
        image_ = load_img(path, target_size=(224, 224))
        image = img_to_array(image_)
        image = image.reshape((1, image.shape[0], image.shape[1], image.shape[2]))
        image = preprocess_input(image)
        yhat = model.predict(image)
        label = decode_predictions(yhat)
        label = label[0][0]
        predictions.append('%s (%.2f%%)' % (label[1], label[2] * 100))

        if label[1] in dog_breeds:
            print('Dog - %s (%.2f%%)' % (label[1], label[2] * 100))
            dogs.append(path)
        elif label[1] in cat_breeds:
            print('cat - %s (%.2f%%)' % (label[1], label[2] * 100))
            cats.append(path)
        else:
            print('%s (%.2f%%)' % (label[1], label[2] * 100))
            misc.append(path)

    results = []
    for i in range(len(predictions)):
        results.append([filenames[i], predictions[i]])

    context = {
        "results": results,
        "predictions": predictions,
        "filenames": filenames,
        "dogs": dogs,
        "no_dogs": len(dogs),
        "no_cats": len(cats),
        "no_misc": len(misc),
        "cats": cats,
        "misc": misc,
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
