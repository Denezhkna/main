from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.response import Response
from api.models import models_all, models_scan
from api.serializers import serializers_all, serializers_scan
import uuid
from pathlib import Path
from api.views.parametrs import COPY_FOLDER_PATH, TESTING_COPY_FOLDER_PATH
import shutil
import os
from api.views.scan import test_scan
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from api.views import change_image, print
import time

# Create your views here.
#норм параметры для сканирования 150x210
#сканируем 2 изображения, объединяем в 1 pdf, отправляем на принт с параметром "number-up":"2"
@csrf_exempt
@api_view(['GET'])
def copy_get_params(request):
    #создаем ид сессии 
    clear_folder_copy()
    id_session = str(uuid.uuid4())
    create_session(id_session)
    #параметры печати
    price_copy = params_price_copy()
    data = {'id_session':id_session,
            'params':price_copy} 
    return Response(
                data,
                status=status.HTTP_200_OK
            )

@api_view(['POST'])
def start_simple_copy(request):
    data = request.data
    if 'id_session' not in data:
        return Response({"res": "Заполните ид сессии"},
                    status=status.HTTP_200_OK
            )
    
    id_session = data['id_session']
 
    #простое сканирование с возможностью двусторонней печати
    user_folder = COPY_FOLDER_PATH+id_session+"/"
    br_x = 320.
    br_y = 200.

    if 'debug' in request.data and request.data['debug'] == True:
        time.sleep(5)
        shutil.copy(TESTING_COPY_FOLDER_PATH+"1.jpg", user_folder)
        shutil.copy(TESTING_COPY_FOLDER_PATH+"2.jpg", user_folder)
        data_file = ["1.jpg","2.jpg"]
    else:
        data_file = test_scan(user_folder = user_folder,id_session = str(id_session), br_x = br_x, br_y = br_y)
    file_name = data_file[0]
    count_copy = 1
    if 'count_copy' in data:
        count_copy = data['count_copy']

    #номер скана (при двусторонней печати 2 итерации)
    number_scan = None
    
    if 'number_scan' in data:
        number_scan = data['number_scan']

    #по дефолту односторонняя
    type_print_file_side = 'one-sided'
    if 'type_print' in data:
        type_print = data['type_print']
        if type_print == 'two':
            type_print_file_side = 'two-sided-long-edge'
            #если двусторонняя, объединяем файлы в 1
            if number_scan == 2:
                file_name = change_image.convert_images_to_one_pdf(id_session = id_session, user_folder = user_folder)
    
    res = None

    if 'debug' in request.data and request.data['debug'] == True:
        time.sleep(5)
        return Response(
                {"id_session":id_session,
                "res":"Готово"},
                    status=status.HTTP_200_OK
            )

    if type_print_file_side == 'one-sided' or type_print == 'two' and number_scan == 2:
        res = print.print_file(identification_doc=False, user_folder = user_folder, file_name=file_name, type_print_file_side = type_print_file_side, count_copy = count_copy)
    return Response(
                {"id_session":id_session,
                "res":res},
                    status=status.HTTP_200_OK
            )

#подразумевается делать х2 
@api_view(['POST'])
def start_identification_copy(request):
    data = request.data
    if 'id_session' not in data:
        return Response({"res": "Заполните ид сессии"},
                    status=status.HTTP_200_OK
            )
    
    id_session = data['id_session']

    #сканирование удостоверений личности (2 А5 на 1 А4)
    user_folder = COPY_FOLDER_PATH+id_session+"/"

    if 'debug' in request.data and request.data['debug'] == True:
        time.sleep(5)
        shutil.copy(TESTING_COPY_FOLDER_PATH+"11.jpg", user_folder)
        shutil.copy(TESTING_COPY_FOLDER_PATH+"22.jpg", user_folder)
        return Response(
                {   'id_session':id_session,
                    'res':["11.jpg", "22.jpg"]},
                status=status.HTTP_200_OK
            ) 

    br_x = 150.
    br_y = 210.
    res = test_scan(user_folder = user_folder,id_session = str(id_session), br_x = br_x, br_y = br_y)
    return Response(
                {   'id_session':id_session,
                    'res':res},
                status=status.HTTP_200_OK
            ) 

@api_view(['POST'])
def print_identification_copy(request):
    if 'debug' in request.data and request.data['debug'] == True:
        time.sleep(5)
        return Response(
                {   'res':"Готово"},
                status=status.HTTP_200_OK
            ) 

    data = request.data
    if 'id_session' not in data:
        return Response(
                {  'res':"Параметры не заполнены"},
                status=status.HTTP_200_OK
            ) 
    id_session = data['id_session']
    user_folder = COPY_FOLDER_PATH+id_session+"/"
    
    count_copy = 1
    if 'count_copy' in data:
        count_copy = data['count_copy']


    #объединяем файлы в 1
    file_name = change_image.convert_images_to_one_pdf(id_session = id_session, user_folder = user_folder)
    #печатаем
    type_print_file_side = 'one-sided'
    res = print.print_file(identification_doc = True, user_folder = user_folder, file_name=file_name, type_print_file_side = type_print_file_side, count_copy = count_copy)
    return Response(
            {"res":res},
                status=status.HTTP_200_OK
        )

@api_view(['DELETE'])
def delete_copy(request):
    data = request.data
    params_list = ['id_session', 'image_name']
    check_params = check_params_fill(data=data, params_list=params_list)
    if not check_params:
        return Response(
                {   'res':"Параметры не заполнены"},
                status=status.HTTP_200_OK
            )
    id_session = data['id_session']
    image_name = data['image_name']
    image_path = COPY_FOLDER_PATH+id_session+"/"+image_name
    if os.path.exists(image_path):
        #удаляем, возвращаем [] image
        os.remove(image_path)
    user_folder = COPY_FOLDER_PATH+id_session+"/"
    data_scan = get_all_copy_from_user(id_session=id_session, user_folder=user_folder)
    return Response(
                {  'id_session':id_session,
                 'res':data_scan},
                status=status.HTTP_200_OK
            )

def get_all_copy_from_user(id_session, user_folder):
    data = []

    for f in os.listdir(user_folder):    
        full_file_name = os.path.join(user_folder, f)
        file_path_name, file_extension = os.path.splitext(full_file_name)
        if os.path.isfile(full_file_name) and file_extension == '.jpg':
            data.append(f)

    data.sort(key=lambda x: int(x.replace(".jpg", "")))

    return data

def check_params_fill(data, params_list):
    if len(data) == 0:
        return False
    for param in params_list:
        if param not in data:
            return False
    return True

def chech_session(request):
    data = request.data
    if 'id_session' in data:
        id_session = data['id_session']
        if os.path.exists(COPY_FOLDER_PATH+str(id_session)):
            return id_session
        else:
            create_session(id_session)
            return id_session
    else:
        id_session = str(uuid.uuid4())
        create_session(id_session)
        return id_session

def params_type_operation_id_copy():
    try:
        type_operation_id = models_all.TypeOperation.objects.filter(name__in = ('copy-one-side','copy-two-side')).values('id')
    except:
        type_operation_id = None

    return type_operation_id

def params_price_copy():
    type_operation_id = params_type_operation_id_copy()
    #data_price = []
    data_dict = {}
    try:
        price = models_all.Prices.objects.filter(type_operation__in = type_operation_id)
        data_prices = serializers_all.PriceSerializer(price, many = True).data
        #ни разу не костыль
        for d_price in data_prices:
            data_dict[d_price["operation"]["name"]] = d_price["price"]
        #data_price.append(data_dict)
    except:
        data_dict = []

    return data_dict

def create_session(id_session):
    #проверка даты папок, удаление старых (где дата > суток)
    clear_folder_copy()
    #папка с ид
    Path(COPY_FOLDER_PATH+str(id_session)).mkdir(parents=True, exist_ok=True)

def clear_folder_copy():
    data_clear = datetime.now() - timedelta(days = 1)
    for root, dirs, files in os.walk(COPY_FOLDER_PATH):
        for dir in dirs:
            date_folder = datetime.fromtimestamp(os.path.getctime(COPY_FOLDER_PATH+dir))
            if date_folder < data_clear:
            #print(datetime.fromtimestamp(dd).strftime("%Y-%m-%D %H:%M:%S"))
                shutil.rmtree(COPY_FOLDER_PATH+dir)