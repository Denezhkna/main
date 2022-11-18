from rest_framework import serializers
from .models import ScanFormat, ScanSaveType, ScanType, Prices, TypeOperation

class ApiSerializer(serializers.ModelSerializer):
    class Meta:
        fieleds = ["action"]

class ScanFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanFormat
        fields = ("name",)

class ScanSaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanSaveType
        fields = ("name",)

class ScanTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanType
        fields = ("name",)       

class TypeOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOperation
        fields = ("name",) #id "id"


class ScanPriceSerializer(serializers.ModelSerializer):
    operation = TypeOperationSerializer(source = 'type_operation', read_only=True)

    class Meta:
        
        model = Prices
        fields = ("operation", "price")  #id "type_operation"       

 

    