from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from django.http.response import JsonResponse
from rest_framework.response import Response
from api.models import models_all
#from . import serializers
import uuid
from pathlib import Path
from api.views.parametrs import SCAN_FOLDER_PATH
import shutil
import os
#import sane
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

# Create your views here.
#токен и все такое
#изменение цен
@api_view
def get_all_options(request):
    return Response(
                {'res':""},
                status=status.HTTP_200_OK
            )