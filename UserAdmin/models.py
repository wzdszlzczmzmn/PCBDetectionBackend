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
    empno = models.CharField(max_length=10, unique=True, editable=False, default='')  # 工号

    def save(self, *args, **kwargs):
        if self.role == 'worker':
            self.empno = self.generate_empno_worker()
        else:
            self.empno = self.generate_empno_admin()

        super().save(*args, **kwargs)

    @staticmethod
    def generate_empno_worker():
        worker_num = User.objects.filter(role='worker').count()

        return f'W{worker_num + 1:04d}'

    @staticmethod
    def generate_empno_admin():
        admin_num = User.objects.filter(role='admin').count()

        return f'A{admin_num + 1:04d}'

