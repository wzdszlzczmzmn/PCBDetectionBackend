from .models import DataTable
from django.db.models import Sum, Value, F, ExpressionWrapper, fields
from datetime import datetime, timedelta
from django.db.models import Avg


def filter_by_line_and_date(start_date, end_date, line_no=None):
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    if line_no is None:
        return DataTable.objects.filter(date__range=(start_date, end_date))
    else:
        return DataTable.objects.filter(date__range=(start_date, end_date), line_no=line_no)


def get_pass_rate(start_date, end_date, line_no=None):
    data_table = filter_by_line_and_date(start_date, end_date, line_no)


def cal_amount_typeSpec(start_date, end_date, defect_type, line_no=None):
    """
    查询某个缺陷的数量，可指定生产线
    参数：(起始日期，结束日期，缺陷种类，[生产线编号])
    返回：字典： result:结果
    """
    data_table = filter_by_line_and_date(start_date, end_date, line_no)
    if line_no is not None:
        data_table = data_table.filter(line_no=line_no)

    res = data_table.values_list(defect_type, flat=True)
    return {
        "result": list(res)
    }


def cal_ratio_statical(start_date, end_date, defect_type, line_no=None):
    """
    计算某个缺陷的占比，指定缺陷种类，可指定生产线
    参数(起始)
    """
    data_table = filter_by_line_and_date(start_date, end_date, line_no)
    categories = data_table.values_list('date', flat=True)
    sums = data_table.aggregate(total=Sum('total_pcb_amount'))
    target_defect_sum = data_table.aggregate(defect_amount=Sum(defect_type))
    ratio = target_defect_sum['defect_amount'] / sums['total']

    return {
        "result": ratio,
        "categories": categories,
    }


def cal_ratio_list(start_date, end_date, defect_type, line_no=None):
    data_table = filter_by_line_and_date(start_date, end_date, line_no)
    grouped_data = data_table.values('date').annotate(
        total_sum=ExpressionWrapper(Sum(F('mh') + F('oc') + F('sh') + F('spc') + F('sp')),
                                    output_field=fields.IntegerField()),
        defect_sum=Sum(defect_type)
    ).order_by('date')  # 根据日期排序

    # 计算两个和的商并返回仅包含比例值的列表
    ratios = [item['defect_sum'] / item['total_sum'] if item['total_sum'] else None for item in grouped_data]
    return [int(num * 1000) / 1000 for num in ratios]


def getProductLineList():
    return DataTable.objects.values_list('line_no', flat=True).distinct()


def get_categories(start_date, end_date, line_no=None):
    data_table = filter_by_line_and_date(start_date, end_date, line_no)
    return list(data_table.values_list('date', flat=True).distinct())


def defect_type(need_translation = False):
    if need_translation:
        return {
            "缺孔": "mh",
            "鼠咬": "mb",
            "开路": "oc",
            "短路": "sh",
            "尖角线": "sp",
            "多余铜": "spc",
            "mh": "缺孔",
            "mb": "鼠咬",
            "oc": "开路",
            "sh": "短路",
            "sp": "尖角线",
            "spc": "多余铜",
        }
    else:
        return ["mh", "mb", "oc", "sh", "sp", "spc"]


def convert_line_no(line_no):  # line_no转为格式为 生产线1 的字符串
    return "生产线{}".format(line_no)


def cal_pass_rate(start_date, end_date, line_no=None):
    data_table = filter_by_line_and_date(start_date, end_date, line_no)
    if line_no is not None:
        pass_rates = data_table.values_list('perfect_rate', flat=True)
        return [int(num * 1000) / 1000 for num in list(pass_rates)]


def get_amount_list(start_date, end_date, line_no=None):
    data_table = filter_by_line_and_date(start_date, end_date, line_no)
    if line_no is not None:
        per = data_table.values_list('perfect_rate', flat=True).distinct()
        de = data_table.annotate(
            modified_rate=Value(1) - F('perfect_rate')
        ).values_list('modified_rate', flat=True).distinct()

        return {
            "total_perfect_pcb_amount": [int(num * 1000) / 1000 for num in list(per)],
            "total_defective_pcb_amount":  [int(num * 1000) / 1000 for num in list(de)]
        }
    else:
        daily_totals = data_table.values('date').annotate(
            daily_pcb_sum=Sum('total_perfect_pcb_amount'),
            daily_defective_sum=Sum('total_defective_pcb_amount')
        ).order_by('date')

        pcb_totals = []
        defective_totals = []

        current_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        totals_dict = {item['date']: (item['daily_pcb_sum'], item['daily_defective_sum']) for item in daily_totals}

        while current_date <= end_date:
            sums = totals_dict.get(current_date, (0, 0))
            pcb_totals.append(sums[0])
            defective_totals.append(sums[1])
            current_date += timedelta(days=1)

        # 将两个列表放入字典返回
        return {
            'total_perfect_pcb_amount': pcb_totals,
            'total_defective_pcb_amount': defective_totals
        }