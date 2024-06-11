from django.db import models

from django.db import models
from django.db.models import Sum, Count, IntegerField, Max
from django.db.models.expressions import Case, When
from django.db.models.functions import TruncDate
from django.db import transaction

from product.models import PCB


class DataTable(models.Model):
    date = models.DateField()
    total_pcb_amount = models.IntegerField(default=0)
    total_perfect_pcb_amount = models.IntegerField(default=0)
    total_defective_pcb_amount = models.IntegerField(default=0)
    perfect_rate = models.FloatField(default=0)
    line_no = models.IntegerField(default=0)
    mh = IntegerField(models.IntegerField(default=0), default=[])
    mb = IntegerField(models.IntegerField(default=0), default=[])
    oc = IntegerField(models.IntegerField(default=0), default=[])
    sh = IntegerField(models.IntegerField(default=0), default=[])
    sp = IntegerField(models.IntegerField(default=0), default=[])
    spc = IntegerField(models.IntegerField(default=0), default=[])

    @classmethod
    def update_perfect_rates(cls):
        # 获取所有DataTable的记录
        all_data_records = DataTable.objects.all()

        # 遍历每条记录并更新合格率
        for record in all_data_records:
            if record.total_pcb_amount > 0:
                # 计算合格率
                perfect_rate = record.total_perfect_pcb_amount / record.total_pcb_amount
            else:
                # 如果没有总数，合格率为0
                perfect_rate = 0

            # 更新合格率
            record.perfect_rate = perfect_rate
            record.save()  # 保存更改

        print("Perfect rates updated for all records.")

    @classmethod
    def update(cls):
        latest_pcb_date = PCB.objects.aggregate(latest_date=Max('record_time'))['latest_date']
        if latest_pcb_date:
            latest_pcb_date = latest_pcb_date.date()  # 将DateTime转换为Date，如果record_time是DateTimeField
        if DataTable.objects.filter(date=latest_pcb_date).exists():
            print("Data for the latest date already processed.")
        with transaction.atomic():
            # 使用 TruncDate 将 record_time 截断为日期
            aggregated_values = PCB.objects.annotate(
                record_time_=TruncDate('record_time')
            ).values('record_time_', 'line_no').annotate(
                mh_sum=Sum('mh'),
                mb_sum=Sum('mb'),
                oc_sum=Sum('oc'),
                sh_sum=Sum('sh'),
                sp_sum=Sum('sp'),
                spc_sum=Sum('spc'),
                total_pcb_amount=Count('id'),  # 计算总行数
                total_perfect_pcb_amount=Count(Case(When(has_defect=True, then=1))),  # 计算布尔字段为true的行数
                total_defective_pcb_amount=Count(Case(When(has_defect=False, then=1))),  # 计算布尔字段为false的行数
                # perfect_rate=Count(Case(When(has_defect=True, then=1))) / Count('id')
            )
            for item in aggregated_values:
                if item['total_pcb_amount'] > 0:
                    perfect_rate = item['total_perfect_pcb_amount'] / item['total_pcb_amount']
                else:
                    perfect_rate = 0
                DataTable.objects.create(
                    date=item['record_time_'],
                    line_no=item['line_no'],
                    mh=item['mh_sum'],
                    mb=item['mb_sum'],
                    oc=item['oc_sum'],
                    sh=item['sh_sum'],
                    sp=item['sp_sum'],
                    spc=item['spc_sum'],
                    total_pcb_amount=item['total_pcb_amount'],
                    total_perfect_pcb_amount=item['total_perfect_pcb_amount'],
                    total_defective_pcb_amount=item['total_defective_pcb_amount'],
                    perfect_rate=perfect_rate,
                )

            DataTable.update_perfect_rates()
