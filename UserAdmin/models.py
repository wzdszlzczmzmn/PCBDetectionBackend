from django.db import models

# Create your models here.
import uuid

from django.db import models


class User(models.Model):
    UUID = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID
    username = models.CharField(max_length=30, unique=True)  # 用户名
    password = models.CharField(max_length=200)  # 用户密码
    is_deleted = models.BooleanField(default=False)  # 是否已经注销
    role = models.CharField(max_length=10, default='worker')  # 身份
    full_name = models.CharField(max_length=30, default='')  # 姓名
    email = models.EmailField(unique=True)  # 用户邮箱
    deviceUUID = models.UUIDField(editable=True, null=True)

