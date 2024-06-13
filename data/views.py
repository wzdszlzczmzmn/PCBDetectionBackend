import pandas

from . import models
from . import calculation

from django.db import DatabaseError
from django.db.models import Sum, F

from data.models import DataTable

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from UserAdmin.utils.JWTUtil import decode_jwt


def update():
    models.DataTable.update()


# Create your views here.
@api_view(['GET'])
def get_product_status(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    if payload['role'] != 'admin':
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    # 返回残次品和良品数量
    start_date = request.query_params.get('startTime')
    end_date = request.query_params.get('endTime')
    line_no = request.query_params.get('productLineId')

    if not start_date or not end_date:
        return Response({'errorInfo': '请求时间有误'}, status=status.HTTP_400_BAD_REQUEST)

    date_range = pandas.date_range(start=start_date, end=end_date, freq='D')
    categories = date_range.strftime('%Y-%m-%d').tolist()

    series = [{'name': '良品', 'data': []}, {'name': '残次品', 'data': []}]

    try:
        if line_no:
            query_set = DataTable.objects.filter(date__range=(start_date, end_date), line_no=line_no).order_by(
                'date').values('total_perfect_pcb_amount', 'total_defective_pcb_amount')

            for item in query_set:
                series[0]['data'].append(item['total_perfect_pcb_amount'])
                series[1]['data'].append(item['total_defective_pcb_amount'])
        else:
            query_set = DataTable.objects.filter(date__range=(start_date, end_date)).values(
                'date').annotate(
                perfect_count=Sum('total_perfect_pcb_amount'),
                defective_count=Sum('total_defective_pcb_amount')).order_by('date')

            for item in query_set:
                series[0]['data'].append(item['perfect_count'])
                series[1]['data'].append(item['defective_count'])

    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'categories': categories, 'series': series}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_product_line_list(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    if payload['role'] != 'admin':
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    start_time_str = request.query_params.get('startTime')
    end_time_str = request.query_params.get('endTime')

    try:
        product_line_list = DataTable.objects.filter(date__range=(start_time_str, end_time_str)).values_list(
            'line_no', flat=True).distinct()
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    product_line_list = list(product_line_list)
    product_line_list.sort()

    return Response({'productLineList': product_line_list}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_defect_status(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    if payload['role'] != 'admin':
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    start_time = request.query_params.get('startTime')
    end_time = request.query_params.get('endTime')
    product_line_id = request.query_params.get('productLineId')
    percentage = True if request.query_params.get('percentage') == '0' else False
    defect_type = request.query_params.get('defectType')

    defect_name_dict = {
        "mh": "缺孔",
        "mb": "鼠咬",
        "oc": "开路",
        "sh": "短路",
        "sp": "尖角线",
        "spc": "多余铜",
    }
    filter_dict = {}

    if not start_time or not end_time:
        return Response({'errorInfo': '请求时间有误'}, status=status.HTTP_400_BAD_REQUEST)

    filter_dict['date__range'] = (start_time, end_time)

    if product_line_id:
        filter_dict['line_no'] = product_line_id

    try:
        query_set = DataTable.objects.filter(**filter_dict).values('date').annotate(
            total_mh=Sum('mh'), total_mb=Sum('mb'), total_oc=Sum('oc'), total_sh=Sum('sh'), total_sp=Sum('sp'),
            total_spc=Sum('spc')).annotate(
            total_amount=F('total_mh') + F('total_mb') + F('total_oc') + F('total_sh') + F('total_sp') + F('total_spc')
        ).order_by('date')

        if defect_type:
            series = [{'name': defect_name_dict[defect_type], 'data': []}]
            for item in query_set:
                if percentage:
                    series[0]['data'].append(round(item['total_' + defect_type] / item['total_amount'] * 100, 1))
                else:
                    series[0]['data'].append(item['total_' + defect_type])
        else:
            series = [{'name': '缺孔', 'data': []}, {'name': '鼠咬', 'data': []}, {'name': '开路', 'data': []},
                      {'name': '短路', 'data': []}, {'name': '尖角线', 'data': []}, {'name': '多余铜', 'data': []}]
            for item in query_set:
                if percentage:
                    series[0]['data'].append(round(item['total_mh'] / item['total_amount'] * 100, 1))
                    series[1]['data'].append(round(item['total_mb'] / item['total_amount'] * 100, 1))
                    series[2]['data'].append(round(item['total_oc'] / item['total_amount'] * 100, 1))
                    series[3]['data'].append(round(item['total_sh'] / item['total_amount'] * 100, 1))
                    series[4]['data'].append(round(item['total_sp'] / item['total_amount'] * 100, 1))
                    series[5]['data'].append(round(item['total_spc'] / item['total_amount'] * 100, 1))
                else:
                    series[0]['data'].append(item['total_mh'])
                    series[1]['data'].append(item['total_mb'])
                    series[2]['data'].append(item['total_oc'])
                    series[3]['data'].append(item['total_sh'])
                    series[4]['data'].append(item['total_sp'])
                    series[5]['data'].append(item['total_spc'])

    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    date_range = pandas.date_range(start=start_time, end=end_time, freq='D')
    categories = date_range.strftime('%Y-%m-%d').tolist()

    return Response({'categories': categories, 'series': series}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_yield_status(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    if payload['role'] != 'admin':
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    start_date = request.query_params.get('startTime')
    end_date = request.query_params.get('endTime')
    line_no = request.query_params.get('productLineId')

    if not start_date or not end_date:
        return Response({'errorInfo': '请求时间有误'}, status=status.HTTP_400_BAD_REQUEST)

    series = []

    try:
        if line_no:
            yield_query_set = DataTable.objects.filter(date__range=(start_date, end_date), line_no=int(line_no))
            yield_list = []

            for item in yield_query_set:
                yield_list.append(round(item.perfect_rate * 100, 1))

            series.append({'name': '生产线' + line_no, 'data': yield_list})
        else:
            product_line_list = DataTable.objects.filter(date__range=(start_date, end_date)).values_list(
                'line_no', flat=True).distinct()

            product_line_list = list(product_line_list)
            product_line_list.sort()

            for item in product_line_list:
                series.append({'name': '生产线' + str(item), 'data': []})

            yield_query_set = DataTable.objects.filter(date__range=(start_date, end_date)).order_by('date')

            for item in yield_query_set:
                series[item.line_no - 1]['data'].append(round(item.perfect_rate * 100, 1))
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    date_range = pandas.date_range(start=start_date, end=end_date, freq='D')

    categories = date_range.strftime('%Y-%m-%d').tolist()

    return Response({'categories': categories, 'series': series}, status=status.HTTP_200_OK)
