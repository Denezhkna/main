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
    path('get_scan/', csrf_exempt(views_scan.get_scan)),
    path('scan_get_params/', csrf_exempt(views_scan.scan_get_params)),
    path('change_rotate_image/', views_scan.change_rotate_image),
    path('get_pdf/', views_scan.get_pdf),
    path('delete_scan/', views_scan.delete_scan),
    path('get_type_save_file/', views_scan.get_type_save_file)
    #path('writehistory/', views_scan.write_history),
    #path('get_all_options/', views_all.get_all_options)
]
