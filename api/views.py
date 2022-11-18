from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.response import Response
from .models import ScanFormat, ScanType, ScanSaveType, Prices, TypeOperation, Session
from .serializers import ScanFormatSerializer, ScanTypeSerializer, ScanSaveTypeSerializer, ScanPriceSerializer, TypeOperationSerializer
import uuid
from pathlib import Path
from .parametrs import SCAN_FORDER_PART
import shutil
import os
import sane
from .scan import test_scan
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
@api_view(['POST'])
def scan_get_forder_path(request):
    data = request.data
    if 'id_session' not in data:
        return Response(
                {"res":"Задайте значение id_session"},
                status=status.HTTP_204_NO_CONTENT
            )

    id_session = data['id_session']
    #ищем папку сессии
    if not os.path.exists(SCAN_FORDER_PART+str(id_session)):
        return Response(
                {"res":"Папка пользователя не найдена"},
                status=status.HTTP_204_NO_CONTENT
            )
    #папка с ид
    #Path(SCAN_FORDER_PART+str(id_session)).mkdir(parents=True, exist_ok=True)
    #сканирование
    #print(SCAN_FORDER_PART+str(id_session))
    res = test_scan(SCAN_FORDER_PART+str(id_session))
    return Response(
                {'res':res},
                status=status.HTTP_200_OK
            )


@api_view(['POST'])
def action(request):

    data = request.data
    action = request.data.get('name')

    if 'name' not in data:
        return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    if action == 'scan':
        data_session = scan_get_params_json(action)
        #возват ид
        return Response(
                data_session,
                status=status.HTTP_200_OK
            )
    elif action == 'print':
        return Response(
                {'res':'принт в разработке'},
                status=status.HTTP_204_NO_CONTENT
            )
    elif action == 'copy':
        return Response(
                {'res':'копи в разработке'},
                status=status.HTTP_204_NO_CONTENT
            )
    else:
        return Response(
                {'res':'действие не найдено'},
                status=status.HTTP_204_NO_CONTENT
            )           

@api_view(['POST'])
def write_history(request):
    info_session = request.data
    if 'id_session' not in info_session:
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

    new_history = Session.objects.create(
        id_session = info_session['id_session'],
        format = info_session['format'] if 'format' in info_session else None,
        operation = info_session['operation'] if 'operation' in info_session else None,
        save_type = info_session['save_type'] if 'save_type' in info_session else None)
    new_history.save()

    return Response(
                status=status.HTTP_200_OK
            )

@csrf_exempt
@api_view(['POST'])
def scan_get_params(request):
    action_value = 'scan'
    #проверяем есть ли старые папки-сессии, удаляем
    clear_forder_scan()
    #создаем ид сессии 
    id_session = uuid.uuid4()
    #папка с ид
    Path(SCAN_FORDER_PART+str(id_session)).mkdir(parents=True, exist_ok=True)
    #параметры печати
    params_scan = scan_get_params_json(action_value)
    
    #print(scan_param)

    data = {'id_session':id_session,
            'params':params_scan} 
    return Response(
                data,
                status=status.HTTP_200_OK
            )
    
    
def clear_forder_scan():
    for root, dirs, files in os.walk(SCAN_FORDER_PART):
        for dir in dirs:
            shutil.rmtree(SCAN_FORDER_PART+dir)

def scan_get_params_json(action_value):
    format = ScanFormat.objects.all()
    data_format = ScanFormatSerializer(format, many=True).data

    type = ScanType.objects.all()
    data_type = ScanTypeSerializer(type, many=True).data

    try:
        type_operation_id = TypeOperation.objects.filter(name__in = (action_value,)).values('id')
    except:
        type_operation_id = None
       
    try:
        price = Prices.objects.filter(type_operation__in = type_operation_id)
        data_price = ScanPriceSerializer(price, many = True).data
    except:
        data_price = []
     
    
    save_type = ScanSaveType.objects.all()
    data_save_type = ScanSaveTypeSerializer(save_type, many=True).data

    data = {'format':data_format, 'type':data_type, 'save_type':data_save_type, 'price':data_price}
    return data