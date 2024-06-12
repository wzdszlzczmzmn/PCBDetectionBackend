import uuid

from django.db import models

# Create your models here.

from datetime import datetime
import pytz
import uuid

from django.db import models


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)  # 任务编号
    is_assign = models.BooleanField(default=False)
    is_finish = models.BooleanField(default=False)
    assign_time = models.DateTimeField(default=None, null=True, blank=True)  # 分配的时间
    finish_time = models.DateTimeField(default=None, null=True, blank=True)  # 完成的时间
    assign_worker = models.ForeignKey('UserAdmin.User', on_delete=models.SET_NULL, null=True, blank=True,
                                      default=None)  # 分配的工人
    pcb = models.ForeignKey('product.PCB', on_delete=models.CASCADE)  # 该任务所涉及到的PCB板
