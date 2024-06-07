"""PCBDetectionBackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework import routers
from django.contrib import admin
from django.urls import path

import UserAdmin.views
import demo.views

router = routers.DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),

    path("test/", demo.views.test),
    path("testPicture/", demo.views.picture_test),
    path("getPicture/", demo.views.picture_get_test),


    # UserAdmin中的url
    path("login/", UserAdmin.views.login),
    path("register/", UserAdmin.views.register),

]
