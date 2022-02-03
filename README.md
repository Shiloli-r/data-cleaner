# data-cleaner

A data cleaning Web App

## How to run
Install python <br>
clone the repository <br>
open Terminal/ powershell on the root of the project <br>
install virtualenv package - `pip install virtualenv` <br>
create a virtual environment - `virtualenv env` <br>
activate the virtual env `env\Scripts\activate` (for windows) <br>
install dependencies - run `pip install -r requirements.txt` <br>
change directory to cleaner  `cd cleaner`  <br>
make migrations - `python manage.py makemigrations`  <br>
migrate - `python manage.py migrate`  <br>
create superuser - `python manage.py createsuperuser`  <br>
start server - `python manage.py runserver`  <br>
open browser at `localhost:8000`  <br>
access admin panel at `localhost:8000/admin`  <br>

## How it Works
<ul>
 <li>Sign up to the site - you will be logged in automatically </li>
 <li>Log in (if you are already registered)</li>
 <li>Upload a dataset file (csv or excel file)</li>
 <li>Clean the data and download the file when done </li>
</ul>

