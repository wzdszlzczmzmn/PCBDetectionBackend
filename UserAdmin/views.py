import traceback

from django.contrib.auth.hashers import make_password, check_password
from django.db import Error, DatabaseError
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from UserAdmin.models import User

from UserAdmin.utils.JWTUtil import generate_access_jwt


@api_view(['POST'])
def login(request):
    user_name = request.data.get('userName')
    password = request.data.get('password')
    if User.objects.filter(username=user_name).exists():
        user = User.objects.get(username=user_name)
        if user.is_deleted:
            return Response({"errorInfo": "用户已注销"}, status=status.HTTP_401_UNAUTHORIZED)

        is_valid = check_password(password, user.password)
        if is_valid:
            token = generate_access_jwt(user)
            response_dict = {'token': token, 'username': user.username, 'fullName': user.full_name, 'email': user.email,
                             'role': user.role, 'empno': user.empno}

            return Response(response_dict)

    return Response({'errorInfo': '账号或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def register(request):
    user_name = request.data.get('userName')
    password = request.data.get('password')
    encrypted_password = make_password(password)
    full_name = request.data.get('fullName')
    email = request.data.get('email')

    if User.objects.filter(username=user_name).exists():
        return Response({"errorInfo": "用户名已被注册"}, status=status.HTTP_409_CONFLICT)
    elif User.objects.filter(email=email).exists():
        return Response({"errorInfo": "邮箱已被使用"}, status=status.HTTP_409_CONFLICT)
    else:
        user = User(username=user_name, password=encrypted_password, full_name=full_name, email=email)
        try:
            user.save()
            token = generate_access_jwt(user)
            token_dict = {"token": token}

            return Response(token_dict)
        except Error:
            traceback.print_exc()

            return Response({"errorInfo": "服务器内部错误"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def modify_self_info(request):
    user_name = request.data.get('username')
    new_full_name = request.data.get('fullName')
    new_email = request.data.get('email')

    if user_name is None or new_full_name is None or new_email is None:
        return Response({"errorInfo": "修改信息有误"})

    if User.objects.filter(username=user_name).exists():
        user = User.objects.get(username=user_name)
        user.full_name = new_full_name
        if new_email != user.email:
            if User.objects.filter(email=new_email).exists():
                return Response({"errorInfo": "邮箱已被占用"})
            else:
                user.email = new_email
        user.save()

        return Response({"newFullName": new_full_name, "newEmail": new_email})
    else:
        return Response({"errorInfo": "用户不存在"})


@api_view(['POST'])
def modify_self_password(request):
    user_name = request.data.get('username')
    original_password = request.data.get('originalPassword')
    new_password = request.data.get('newPassword')

    if user_name is None or original_password is None or new_password is None:
        return Response({"errorInfo": "修改密码有误"})

    if User.objects.filter(username=user_name).exists():
        user = User.objects.get(username=user_name)
        password = user.password
        is_auth = check_password(original_password, password)
        if is_auth:
            new_password_encrypted = make_password(new_password)
            user.password = new_password_encrypted
            user.save()

            return Response({"info": "修改成功"})
        else:
            return Response({"errorInfo": "原密码错误"})

    else:
        return Response({"errorInfo": "用户不存在"})


@api_view(['POST'])
def logout(request):
    username = request.data.get('username')

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.is_deleted = True
        user.save()

        return Response({"info": "注销成功"})
    else:
        return Response({"errorInfo": "用户不存在"})


@api_view(['GET'])
def get_user_list(request):
    user_type = request.query_params.get('userType')
    user_status = request.query_params.get('userStatus')

    res_list = []
    filter_dict = {}

    if user_type != '':
        filter_dict['role'] = user_type

    if user_status != '':
        filter_dict['is_deleted'] = True if user_status == 'logout' else False

    user_list = User.objects.filter(**filter_dict)

    for user in user_list:
        res_list.append({'UUID': user.UUID, 'fullName': user.full_name, 'role': user.role, 'isDelete': user.is_deleted})

    return Response({'userInfoList': res_list})


@api_view(['GET'])
def get_user_info_uuid(request):
    uuid = request.query_params.get('UUID')

    if uuid != '':
        user = User.objects.get(UUID=uuid)

        return Response({'fullName': user.full_name, 'email': user.email})
    else:
        return Response({'errorInfo': 'UUID不能为空'})


@api_view(['POST'])
def modify_info_uuid(request):
    uuid = request.data.get('UUID')
    new_full_name = request.data.get('fullName')
    new_email = request.data.get('email')
    new_password = request.data.get('password')

    if not uuid:
        return Response({'errorInfo': 'UUID不为空'}, status=status.HTTP_400_BAD_REQUEST)

    if not new_full_name or not new_email:
        return Response({'errorInfo': '修改信息有误'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(UUID=uuid)
    except ObjectDoesNotExist:
        return Response({'errorInfo': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

    if new_email != user.email:
        if User.objects.filter(email=new_email).exists():
            return Response({'errorInfo': '邮箱已被占用'}, status=status.HTTP_400_BAD_REQUEST)

    user.full_name = new_full_name
    user.email = new_email

    if new_password:
        user.password = make_password(new_password)

    try:
        user.save()
    except Error:
        return Response({'errorInfo': '修改失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'info': '修改成功'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def logout_uuid(request):
    uuid = request.data.get('UUID')

    if not uuid:
        return Response({'errorInfo': 'UUID不为空'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(UUID=uuid)
    except ObjectDoesNotExist:
        return Response({'errorInfo': '用户不存在'}, status=status.HTTP_400_BAD_REQUEST)

    user.is_deleted = True

    try:
        user.save()
    except Error:
        return Response({'errorInfo': '修改失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'info': '注销成功'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def add_worker(request):
    username = request.data.get('username')
    full_name = request.data.get('fullName')
    email = request.data.get('email')
    password = request.data.get('password')

    if User.objects.filter(username=username).exists():
        return Response({'errorInfo': '用户名已存在'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({'errorInfo': '邮箱已占用'}, status=status.HTTP_400_BAD_REQUEST)

    user = User(username=username, full_name=full_name, email=email, password=make_password(password))

    try:
        user.save()
    except Error:
        return Response({'errorInfo': '添加失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'info': '添加成功'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_worker_list(request):
    res = []

    try:
        query_set = User.objects.filter(role='worker')

        for item in query_set:
            res.append({'UUID': item.UUID, 'fullName': item.full_name, 'empno': item.empno})
    except DatabaseError:
        return Response({'errorInfo': '服务器内部错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(res, status=status.HTTP_200_OK)
