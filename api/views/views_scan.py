from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.response import Response
from api.models import models_all, models_scan
from api.serializers import serializers_all, serializers_scan
import uuid
from pathlib import Path
from api.views.parametrs import SCAN_FOLDER_PATH, TESTING_SCAN_FOLDER_PATH
import shutil
import os
import sane
from api.views.scan import test_scan
from api.views.send_email import send_email
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from api.views import change_image 
from functools import reduce
import time
import shutil
# Create your views here.

@csrf_exempt
@api_view(['POST'])
def start_scan(request):
    #проверяем сессию, если нет создаем + папка
    id_session = chech_session(request)
    user_folder = SCAN_FOLDER_PATH+id_session+"/"

    if 'debug' in request.data and request.data['debug'] == True:
        time.sleep(5)
        shutil.copy(TESTING_SCAN_FOLDER_PATH, user_folder)
        return Response(
                {   'id_session':id_session,
                    'res':["1.jpg"]},
                status=status.HTTP_200_OK
            )

    #сканирование
    br_x = 320.
    br_y = 200.
    res = test_scan(user_folder = user_folder, id_session = str(id_session),  br_x = br_x, br_y = br_y)
    return Response(
                {   'id_session':id_session,
                    'res':res},
                status=status.HTTP_200_OK
            )    

@csrf_exempt
@api_view(['GET'])
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
def rotate_image(request):
    data = request.data
    params_list = ['id_session', 'image_name', 'angle']
    check_params = check_params_fill(data=data, params_list=params_list)
    if not check_params:
        return Response(
                {   'res':"Параметры не заполнены"},
                status=status.HTTP_200_OK
            )

    image = change_image.image_rotation(id_session = data['id_session'], img_name = data['image_name'], angle = int(data['angle']))
    return Response(
                {   'res':image},
                status=status.HTTP_200_OK
            )

@api_view(['DELETE'])
def delete_scan(request):
    data = request.data
    print(request)
    print("----------------")
    print(data)
    params_list = ['id_session', 'image_name']
    check_params = check_params_fill(data=data, params_list=params_list)
    if not check_params:
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
    user_folder = SCAN_FOLDER_PATH+id_session+"/"
    data_scan = get_all_scan_from_user(id_session=id_session, user_folder=user_folder)
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

@api_view(['POST'])
def save_or_send_scan(request):
    data = request.data

    params_list = ['id_session', 'type_file', 'format_save', 'save']
    check_params = check_params_fill(data=data, params_list=params_list)
    if not check_params:
        return Response (
                {"res":"Не заполнены параметры"},
                status=status.HTTP_200_OK
            )

    id_session = data['id_session']
    user_folder = SCAN_FOLDER_PATH+id_session+"/"

    if data['save']['type'] == 'usb':
        save_type = data['save']['type']
    else: 
        save_type = data['save']['type']
        save_path = data['save']['path']
    
    type_file = data['type_file']
    format_save = data['format_save']
    
    if format_save == '.pdf':
        if type_file == 'one':
            #конверт всех файлов во все .pdf
            data_file_name = change_image.convert_images_to_many_pdf(id_session, user_folder = user_folder)
        else:
            #сборка всех в один pdf
            
            file_name = change_image.convert_images_to_one_pdf(id_session = id_session, user_folder = user_folder)
            data_file_name = [file_name]

    else:
        data_file_name = get_all_scan_from_user(id_session = id_session, user_folder=user_folder)
  
  
    #path_file = SCAN_FOLDER_PATH + id_session + "/" + file_name
  
    state = "Что-то пошло не так, попробуйте другой вариант сохранения или обратитесь к администратору"
    if save_type == "usb":
        user_folder_path = create_folder_in_usb()
        res = save_to_usb(user_folder_path, data_file_name, id_session)
        if res:
            state = "Готово"

    elif save_type == "email":
        res = send_to_email(save_path = save_path, data_file_name = data_file_name, id_session = id_session)
        if res: 
            state = "Готово"
        
    else:
         state = state
    return Response (
                {"res":state},
                status=status.HTTP_200_OK
            )

def create_folder_in_usb():
    corrent_date_time = datetime.now()
    corrent_data = corrent_date_time.strftime("%d-%m-%y")
    save_dir_name = "BOT_SET_"+corrent_data
    usb_path = "/media/bots/"

    for usb in os.listdir(usb_path):
        if os.path.isdir(os.path.join(usb_path, usb)):
            dir = os.path.join(usb_path, usb, save_dir_name)
            if not os.path.exists(dir):
                Path(dir).mkdir(parents=True, exist_ok=True)
            return dir
           

def check_params_fill(data, params_list):
    if len(data) == 0:
        return False
    for param in params_list:
        if param not in data:
            return False
    return True

def save_to_usb(user_folder_path, data_file_name, id_session):
    try:
        session_folder = SCAN_FOLDER_PATH+id_session+"/"
        for file in data_file_name:
            copy_path = shutil.copy(session_folder+file, user_folder_path+"/"+file, follow_symlinks=True)
        return True
    except:
        return False

def send_to_email(save_path, data_file_name, id_session):
    res = send_email(save_path, data_file_name, id_session)
    return res

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
        data_price = serializers_all.PriceSerializer(price, many = True).data
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

def get_all_scan_from_user(id_session, user_folder):
    data = []

    for f in os.listdir(user_folder):    
        full_file_name = os.path.join(user_folder, f)
        file_path_name, file_extension = os.path.splitext(full_file_name)
        if os.path.isfile(full_file_name) and file_extension == '.jpg':
            data.append(f)

    data.sort(key=lambda x: int(x.replace(".jpg", "")))

    return data

def get_new_name_scan(data_scan):
    if len(data_scan) == 0:
        return "1.jpg"
    last_name = reduce(lambda x, y: x if int(x.replace(".jpg", "")) > int(y.replace(".jpg", "")) else y, data_scan)
    new_name = str(int(last_name.replace(".jpg", ""))+1)+".jpg"
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