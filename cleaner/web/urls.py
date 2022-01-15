from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_, name='login'),
    path('signup', views.sign_up, name='signup'),
    path('logout', views.logout, name='logout'),
]
