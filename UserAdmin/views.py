import traceback

from django.contrib.auth.hashers import make_password, check_password
from django.db import Error

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from UserAdmin.models import User

from UserAdmin.utils.JWTUtil import generate_jwt


@api_view(['POST'])
def login(request):
    user_name = request.data.get('userName')
    password = request.data.get('password')
    if User.objects.filter(username=user_name).exists():
        user = User.objects.get(username=user_name)
        is_valid = check_password(password, user.password)
        if is_valid:
            token = generate_jwt(user)
            token_dict = {'token': token}

            return Response(token_dict)

    return Response(status=status.HTTP_401_UNAUTHORIZED)


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
            token = generate_jwt(user)
            token_dict = {"token": token}

            return Response(token_dict)
        except Error:
            traceback.print_exc()

            return Response({"errorInfo": "服务器内部错误"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


