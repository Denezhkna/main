from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.response import Response
from api.models import models_all, models_scan
from api.serializers import serializers_all, serializers_scan
import uuid
from pathlib import Path
from api.views.parametrs import SCAN_FOLDER_PATH
import shutil
import os
import sane
from api.views.scan import test_scan
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from api.views import change_image 
from functools import reduce


# Create your views here.
@api_view(['GET'])
def get_pdf(request):
    data = request.data
    if 'id_session' not in data :
        return Response(
                {   'res':"Параметры не заполнены"},
                status=status.HTTP_200_OK
            )

    name_pdf = change_image.convert_images_to_pdf(id_session = data['id_session'])
    return Response(
                {   'res':name_pdf},
                status=status.HTTP_200_OK
            )    

@csrf_exempt
@api_view(['POST'])
def get_scan(request):
    data = request.data
    #проверяем сессию, если нет создаем + папка
    #мб возвращать ид сессии в ответе
    id_session = chech_session(request)
    #сканирование
    #print(SCAN_FORDER_PART+str(id_session))
    res = test_scan(str(id_session))
    return Response(
                {   'id_session':id_session,
                    'res':res},
                status=status.HTTP_200_OK
            )    

@csrf_exempt
@api_view(['POST'])
def scan_get_params(request):
    #создаем ид сессии 
    id_session = uuid.uuid4()
    create_session(id_session)
    #параметры печати
    price_scan = params_price_scan()
    data = {'id_session':id_session,
            'params':price_scan} 
    return Response(
                data,
                status=status.HTTP_200_OK
            )

@api_view(['POST'])
def change_rotate_image(request):
    data = request.data
    if 'id_session' not in data or 'image_name' not in data or 'angle' not in data:
        return Response(
                {   'res':"Параметры не заполнены"},
                status=status.HTTP_200_OK
            )

    image = change_image.image_rotation(id_session = data['id_session'], img_name = data['image_name'], angle = int(data['angle']))
    return Response(
                {   'res':image},
                status=status.HTTP_200_OK
            )

@api_view(['POST'])
def delete_scan(request):
    data = request.data
    if 'id_session' not in data or 'image_name' not in data:
        return Response(
                {   'res':"Параметры не заполнены"},
                status=status.HTTP_200_OK
            )
    id_session = data['id_session']
    image_name = data['image_name']
    image_path = SCAN_FOLDER_PATH+id_session+"/"+image_name
    if os.path.exists(image_path):
        #удаляем, возвращаем [] image
        os.remove(image_path)
    data_scan = get_all_scan_from_user(id_session=id_session)
    return Response(
                {  'id_session':id_session,
                 'res':data_scan},
                status=status.HTTP_200_OK
            )

@api_view(['GET'])
def get_type_save_file(request):
    data = params_save_type_file_scan()
    return Response(
                {"res":data},
                status=status.HTTP_200_OK
            )

@api_view(['GET'])
def save_pdf(request):
    data = request.data
    if "id_session" not in data or "file_name" not in data or "save" not in data:
        return Response (
                {"res":"Не заполнены параметры"},
                status=status.HTTP_200_OK
            )


    save = data["save"]
    save_type = save['type']
    save_path = save['path']
    file_name = data['file_name']
    id_session = data['id_session']
    path_file = SCAN_FOLDER_PATH + id_session + "/" + file_name
    if not os.path.exists(path=path_file):
        return Response (
                {"res":"Файл не найден"},
                status=status.HTTP_200_OK
            )
    
    if save_type == "usb":
        save_to_usb(save_path)
    elif save_type == "email":
        send_to_email(save_path)
    else:
         return Response (
                {"res":"Параметр типа сохранения задан неверно"},
                status=status.HTTP_200_OK
            )


def save_to_usb(save_path):
    pass

def send_to_email(save_path):
    pass

def params_save_type_file_scan():
    save_type = models_scan.SaveTypeScan.objects.all()
    data_save_type = serializers_scan.SaveTypeScanSerializer(save_type, many=True).data
    return data_save_type

def params_type_operation_id_scan():
    try:
        type_operation_id = models_all.TypeOperation.objects.filter(name__in = ('scan',)).values('id')
    except:
        type_operation_id = None

    return type_operation_id

def params_price_scan():
    type_operation_id = params_type_operation_id_scan()
    try:
        price = models_all.Prices.objects.filter(type_operation__in = type_operation_id)
        data_price = serializers_all.ScanPriceSerializer(price, many = True).data
    except:
        data_price = []

    return data_price

def params_format_scan():
    format = models_scan.FormatScan.objects.all()
    data_format = serializers_scan.FormatScanSerializer(format, many=True).data
    return data_format

def params_type_scan():
    type = models_scan.TypeScan.objects.all()
    data_type = serializers_scan.TypeScanSerializer(type, many=True).data
    return data_type

def chech_session(request):
    data = request.data
    if 'id_session' in data:
        id_session = data['id_session']
        if os.path.exists(SCAN_FOLDER_PATH+str(id_session)):
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
    clear_folder_scan()
    #папка с ид
    Path(SCAN_FOLDER_PATH+str(id_session)).mkdir(parents=True, exist_ok=True)

def clear_folder_scan():
    data_clear = datetime.now() - timedelta(days = 1)
    for root, dirs, files in os.walk(SCAN_FOLDER_PATH):
        for dir in dirs:
            date_folder = datetime.fromtimestamp(os.path.getctime(SCAN_FOLDER_PATH+dir))
            if date_folder < data_clear:
            #print(datetime.fromtimestamp(dd).strftime("%Y-%m-%D %H:%M:%S"))
                shutil.rmtree(SCAN_FOLDER_PATH+dir)

def get_all_scan_from_user(id_session):
    user_path = SCAN_FOLDER_PATH+id_session

    data = []

    for f in os.listdir(user_path):    
        full_file_name = os.path.join(user_path, f)
        file_path_name, file_extension = os.path.splitext(full_file_name)
        if os.path.isfile(full_file_name) and file_extension == '.png':
            data.append(f)

    data.sort(key=lambda x: int(x.replace(".png", "")))

    return data

def get_new_name_scan(data_scan):
    if len(data_scan) == 0:
        return "1.png"
    last_name = reduce(lambda x, y: x if int(x.replace(".png", "")) > int(y.replace(".png", "")) else y, data_scan)
    new_name = str(int(last_name.replace(".png", ""))+1)+".png"
    return new_name


def write_history(id_session, format = None, operation = None, save_type = None, price = None):

    new_history = models_scan.HistoryScan.objects.create(
        id_session = id_session,
        format = format,
        operation = operation,
        save_type = save_type,
        price = price
        )
    new_history.save()