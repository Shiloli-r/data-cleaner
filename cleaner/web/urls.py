from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_, name='login'),
    path('signup', views.sign_up, name='signup'),
    path('logout', views.logout, name='logout'),
    path('clean', views.clean, name='clean'),
    path('clean-images', views.clean_images, name='clean-images')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
