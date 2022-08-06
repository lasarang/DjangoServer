"""miniserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.urls import re_path as url
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from rest_framework import permissions

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    path('users/',include('users.urls')),
    path('external/',include('influxdb.urls')),
    path('info/',include([
        path('cultivo/',include('cultivo.urls')),
        path('finca/',include('finca.urls')),
        path('sensor/',include('sensores.urls')),    
        path('crop/',include('cultivo.urls')),
        path('farm/',include('finca.urls')),   
        path('notifications/',include('notificaciones.urls')),   
    ])),
    path('util/', include('util.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
