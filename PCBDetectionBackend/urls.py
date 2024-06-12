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

import UserAdmin.views
import data.views
import demo.views
import product.views
import task.views

router = routers.DefaultRouter()

urlpatterns = [
    path("admin/", admin.site.urls),

    path("test/", demo.views.test),
    path("testPicture/", demo.views.picture_test),
    path("getPicture/", demo.views.picture_get_test),

    path("addtestdata/", product.views.addTestData),  # 加载数据
    path("dataShow/", include('data.urls')),

    # UserAdmin中的url
    path("login/", UserAdmin.views.login),
    path("register/", UserAdmin.views.register),
    path("userInfo/modifyUserInfo/", UserAdmin.views.modify_self_info),
    path("userInfo/modifyUserPassword/", UserAdmin.views.modify_self_password),
    path("userInfo/logout/", UserAdmin.views.logout),

    path("userAdmin/getUserList/", UserAdmin.views.get_user_list),
    path("userAdmin/getUserInfoUUID/", UserAdmin.views.get_user_info_uuid),
    path("userAdmin/modifyInfoUUID/", UserAdmin.views.modify_info_uuid),
    path("userAdmin/logoutUUID/", UserAdmin.views.logout_uuid),
    path("userAdmin/addWorker/", UserAdmin.views.add_worker),
    path("userAdmin/getWorkerList/", UserAdmin.views.get_worker_list),

    # task中的url
    path("task/getTaskList/", task.views.get_task_list),
    path("task/getTaskDetail/", task.views.get_task_detail),
    path("task/getTaskPicture/", task.views.get_pcb_picture),
    path("task/assignTask/", task.views.assign_task),
    path("task/cancelAssign/", task.views.cancel_assign),
    # path("task/importData", task.views.import_data)

]
