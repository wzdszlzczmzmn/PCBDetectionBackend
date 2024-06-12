from django.db import models


class PCB(models.Model):
    record_time = models.DateTimeField()  # 记录时间
    line_no = models.IntegerField(default=0)  # 生产线
    picture_file_name = models.CharField(max_length=100, default='')
    has_defect = models.BooleanField(default=False)  # 是否具有缺陷
    mh = models.IntegerField(default=0)  # missing hole
    mb = models.IntegerField(default=0)  # mouse bite
    oc = models.IntegerField(default=0)  # open circuit
    sh = models.IntegerField(default=0)  # short
    sp = models.IntegerField(default=0)  # spur
    spc = models.IntegerField(default=0)  # spurious copper
    # task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True)  # 属于的任务

