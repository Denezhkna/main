from rest_framework import serializers
from api.models import models_scan
from . import serializers_all, serializers_copy, serializers_print

class ApiSerializer(serializers.ModelSerializer):
    class Meta:
        fieleds = ["action"]

class FormatScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models_scan.FormatScan
        fields = ("name",)

class SaveTypeScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models_scan.SaveTypeScan
        fields = ("name",)

class TypeScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = models_scan.TypeScan
        fields = ("name",)       

      

 

    