import random

from django.db import DatabaseError
from django.http import FileResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from task.models import Task
from product.models import PCB
from UserAdmin.models import User

import pandas
from datetime import datetime

from UserAdmin.utils.JWTUtil import decode_jwt

@api_view(['GET'])
def import_data(request):
    date_range = pandas.date_range(start='2024-06-01', end='2024-07-01', freq='D')
    categories = date_range.strftime('%Y-%m-%d').tolist()
    for i in range(0, len(categories) - 1):
        start_date = categories[i]
        end_date = categories[i + 1]

        query_set = PCB.objects.filter(record_time__range=(start_date, end_date)).order_by('record_time')

        for item in query_set:
            if random.random() < 0.05:
                task = Task(pcb=item)
                task.save()

    return Response('OK!')


@api_view(['GET'])
def get_task_list(request):
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
    finish_status = request.query_params.get('finishStatus')
    time_order = request.query_params.get('timeOrder')

    if not start_time or not end_time or not time_order:
        return Response({'errorInfo': '请求参数错误'}, status=status.HTTP_400_BAD_REQUEST)

    filter_dict = {'pcb__record_time__range': (start_time, end_time)}

    if finish_status == 'unAssign':
        filter_dict['is_assign'] = False
    elif finish_status == 'unFinish':
        filter_dict['is_finish'] = False
        filter_dict['is_assign'] = True
    elif finish_status == 'finished':
        filter_dict['is_finish'] = True

    try:
        if time_order == 'DES':
            query_set = Task.objects.filter(**filter_dict).order_by('-pcb__record_time')
        else:
            query_set = Task.objects.filter(**filter_dict).order_by('pcb__record_time')

        res = []

        for item in query_set:
            res.append({'id': item.task_id, 'createTime': item.pcb.record_time, 'assignTime': item.assign_time,
                        'finishTime': item.finish_time,
                        'assignWorkerEmpno': item.assign_worker.empno if item.assign_worker is not None else None})
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(res, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_task_detail(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    task_id = request.query_params.get('id')

    if not task_id:
        return Response({'errorInfo': 'ID不为空'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = Task.objects.get(task_id=task_id)
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    res = {'id': task.task_id, 'pipelineNumber': task.pcb.line_no, 'finishTime': task.finish_time,
           'assignTime': task.assign_time, 'createTime': task.pcb.record_time,
           'assignWorkerEmpno': task.assign_worker.empno if task.assign_worker is not None else None,
           'mhCount': task.pcb.mh,
           'mbCount': task.pcb.mb, 'ocCount': task.pcb.oc, 'shCount': task.pcb.sh, 'spCount': task.pcb.sp,
           'spcCount': task.pcb.spc}

    return Response(res, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_pcb_picture(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    task_id = request.query_params.get('id')

    if not task_id:
        return Response({'errorInfo': 'ID不为空'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = Task.objects.get(task_id=task_id)
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    path = task.pcb.picture_file_name

    file_path = './PCB.jpg'
    return FileResponse(open(file_path, 'rb'))


@api_view(['POST'])
def assign_task(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    if payload['role'] != 'admin':
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    uuid = request.data.get('UUID')
    task_id = request.data.get('taskId')

    if not uuid or not task_id:
        return Response({'errorInfo': '请求参数错误'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        worker = User.objects.get(UUID=uuid)
        task = Task.objects.get(task_id=task_id)

        task.assign_worker = worker
        task.assign_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task.is_assign = True
        task.save()
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'info': '分配成功'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def cancel_assign(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    if payload['role'] != 'admin':
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    task_id = request.data.get('taskId')

    if not task_id:
        return Response({'errorInfo': 'ID不为空'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = Task.objects.get(task_id=task_id)

        task.is_assign = False
        task.assign_time = None
        task.assign_worker = None
        task.save()
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'info': '取消成功'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_my_tasks(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    uuid = payload['id']

    start_time = request.query_params.get('startTime')
    end_time = request.query_params.get('endTime')
    finish_status = request.query_params.get('finishStatus')
    time_order = request.query_params.get('timeOrder')

    if not start_time or not end_time or not uuid or not time_order:
        return Response({'errorInfo': '请求参数错误'}, status=status.HTTP_400_BAD_REQUEST)

    filter_dict = {'assign_time__range': (start_time, end_time), 'assign_worker': uuid}

    if finish_status == 'unFinish':
        filter_dict['is_finish'] = False
        filter_dict['is_assign'] = True
    elif finish_status == 'finished':
        filter_dict['is_finish'] = True

    try:
        if time_order == 'ASC':
            query_set = Task.objects.filter(**filter_dict).order_by('assign_time')
        else:
            query_set = Task.objects.filter(**filter_dict).order_by('-assign_time')

        res = []

        for item in query_set:
            res.append({'id': item.task_id, 'createTime': item.pcb.record_time, 'assignTime': item.assign_time,
                        'finishTime': item.finish_time,
                        'assignWorkerEmpno': item.assign_worker.empno if item.assign_worker is not None else None})
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(res, status=status.HTTP_200_OK)


@api_view(['POST'])
def upload_task_picture(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    payload = decode_jwt(auth_header)

    if not payload:
        return Response({'errorInfo': '认证失败'}, status=status.HTTP_401_UNAUTHORIZED)

    task_id = request.data.get('taskId')
    upload_file = request.FILES['file']

    if not task_id:
        return Response({'errorInfo': '请求参数错误'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        task = Task.objects.get(task_id=task_id)

        task.is_finish = True
        task.finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task.save()
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'info': '上传成功'}, status=status.HTTP_200_OK)
