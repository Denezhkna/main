"""test_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from api.views import views_scan, views_copy, views_print, views_all
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('admin/', admin.site.urls),
    path('start_scan/', csrf_exempt(views_scan.start_scan)),
    path('scan_get_params/', csrf_exempt(views_scan.scan_get_params)),
    path('rotate_image/', views_scan.rotate_image),
    path('delete_scan/', views_scan.delete_scan),
    path('get_type_save_file/', views_scan.get_type_save_file),
    path('save_or_send_scan/', views_scan.save_or_send_scan),
    #печать
    path('get_device/', views_print.get_device),
    path('get_file_tree/', views_print.get_file_tree),
    path('create_session_print/', views_print.create_session_print),
    path('preview_file/', views_print.preview_file),
    path('print_file/', views_print.print_file),
    #копирование
    path('print_identification_copy/', views_copy.print_identification_copy),
    path('copy_get_params/', views_copy.copy_get_params),
    path('start_simple_copy/',views_copy.start_simple_copy),
    path('start_identification_copy/',views_copy.start_identification_copy),
    path('delete_copy/', views_copy.delete_copy)
    #path('writehistory/', views_scan.write_history),
    #path('get_all_options/', views_all.get_all_options)
]
