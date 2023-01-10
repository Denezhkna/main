from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.response import Response
from api.models import models_all, models_scan
from api.serializers import serializers_all, serializers_scan
import uuid
from pathlib import Path
from api.views.parametrs import PRINT_FOLDER_PATH
from api.views import print
import shutil
import os
#import sane
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
import time

# Create your views here.
@api_view(['GET'])
def get_device(request):
    
    usb_path = get_usb_path()
    if usb_path == None:
        return Response(
                {"res":None},
                status=status.HTTP_200_OK
              )

    return Response(
            {"res":usb_path},
            status=status.HTTP_200_OK
            )

@api_view(['GET'])
def get_file_tree(request):
    folder = get_usb_path()
    if folder == None:
        return Response(
                {"res":None},
                status=status.HTTP_200_OK
              )

    tree = tree_usb(folder)
    return Response(
                {"res":tree},
                status=status.HTTP_200_OK
              )

@api_view(['POST'])
def create_session_print(request):
    id_session = uuid.uuid4()
    create_session(id_session)
    price_print = params_price_print()
    return Response(
                {"id_session":id_session,
                'params':price_print},
                status=status.HTTP_200_OK
              )

@api_view(['POST'])
def preview_file(request):
    data = request.data
    if 'file_path' not in data or 'id_session' not in data:
        return Response(
            {"res":"Не заполнены параметры"},
                status=status.HTTP_200_OK
        )
    file_path = data['file_path']
    id_session = data['id_session']
    if not os.path.exists(file_path) or not os.path.exists(PRINT_FOLDER_PATH+id_session):
        return Response(
            {"res":"Не найден файл или папка пользователя"},
                status=status.HTTP_200_OK
        )
    #конвер файла в pdf, возврат имени файла
    data_png = print.get_preview_file(id_session=id_session, file_path=file_path)
    return Response(
            {"res":data_png},
                status=status.HTTP_200_OK
        )

@api_view(['POST'])
def print_file(request):
    if 'debug' in request.data and request.data['debug'] == True:
        time.sleep(5)
        return Response(
                {   'res':"Готово"},
                status=status.HTTP_200_OK
            )

    data = request.data
    if 'file_name' not in data or 'id_session' not in data :
        return Response(
            {"res":"Не заполнены параметры"},
                status=status.HTTP_200_OK
        )

    file_name = data['file_name']
    id_session = data['id_session']
    if not os.path.exists(PRINT_FOLDER_PATH+id_session+"/"+file_name):
        return Response(
            {"res":"Не найден файл или папка пользователя"},
                status=status.HTTP_200_OK
        )

    if 'page_list' in data:
        new_file_name = print.create_file_whith_selected_page(id_session = id_session, file_name = file_name, page_list = data['page_list'])
        if new_file_name != None:
            file_name = new_file_name

    #по дефолту односторонняя
    type_print_file_side = 'one-sided'

    if 'type_print' in data:
        type_print = data['type_print']
        if type_print == 'two':
            type_print_file_side = 'two-sided-long-edge'

    count_copy = 1
    if 'count_copy' in data:
        count_copy = data['count_copy']

    user_folder = PRINT_FOLDER_PATH+id_session+"/"
    res = print.print_file(identification_doc=False, user_folder = user_folder, file_name=file_name, type_print_file_side = type_print_file_side, count_copy = count_copy)
    return Response(
            {"res":res},
                status=status.HTTP_200_OK
        )

def params_price_print():
    type_operation_id = params_type_operation_id_print()
    try:
        price = models_all.Prices.objects.filter(type_operation__in = type_operation_id)
        data_price = serializers_all.PriceSerializer(price, many = True).data
    except:
        data_price = []

    return data_price

def params_type_operation_id_print():
    try:
        type_operation_id = models_all.TypeOperation.objects.filter(name__in = ('print-one-side','print-two-side')).values('id')
    except:
        type_operation_id = None

    return type_operation_id

def chech_session(request):
    data = request.data
    if 'id_session' in data:
        id_session = data['id_session']
        if os.path.exists(PRINT_FOLDER_PATH+str(id_session)):
            return id_session
        else:
            create_session(id_session)
            return id_session
    else:
        id_session = uuid.uuid4()
        create_session(id_session)
        return id_session

def create_session(id_session):
    #проверка даты папок, удаление старых (где дата > суток)
    clear_folder_print()
    #папка с ид
    Path(PRINT_FOLDER_PATH+str(id_session)).mkdir(parents=True, exist_ok=True)

def clear_folder_print():
    data_clear = datetime.now() - timedelta(days = 1)
    for root, dirs, files in os.walk(PRINT_FOLDER_PATH):
        for dir in dirs:
            date_folder = datetime.fromtimestamp(os.path.getctime(PRINT_FOLDER_PATH+dir))
            if date_folder < data_clear:
                shutil.rmtree(PRINT_FOLDER_PATH+dir)

def get_usb_path():
    device = f"/media/{os.getlogin()}/"
    folder = Path(device)
    print(folder)
    if len(list(folder.iterdir())) == 0:
        return None
    else:
        for f in folder.iterdir():
            return str(f)
    
def tree_usb(path):
    d = {"name": os.path.basename(path)}
    if os.path.isdir(path):
        d["type"] = "directory"
        d["children"] = [tree_usb(os.path.join(path, x)) for x in os.listdir(path)]
    else:
        d["type"] = "file"
    return d