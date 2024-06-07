from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import FileResponse

# Create your views here.


@api_view(['GET'])
def test(request):
    data = {"data": "You are successfully connect to Django Backend"}
    return Response(data)


@api_view(['POST'])
def picture_test(request):
    data = {'data': 'OK!'}
    print(request.FILES)
    upload_file = request.FILES['file']
    default_storage.save('./uploadPic.jpg', ContentFile(upload_file.read()))

    return Response(data)


@api_view(['GET'])
def picture_get_test(request):
    file_path = './PCB-copy.png'

    return FileResponse(open(file_path, 'rb'))
