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
from django.urls import path, include
from . import views

import UserAdmin.views
import data.views
import demo.views
import product.views

router = routers.DefaultRouter()

urlpatterns = [
    path('getProductStatus/', views.get_product_status, name='getProductStatus'),
    path('getProductLineList/', views.get_product_line_list, name='getProductLineList'),
    path('getDefectStatus/', views.get_defect_status, name='getProductList'),
    path('getYieldStatus/', views.get_yield_status, name='getYieldStatus'),

]
