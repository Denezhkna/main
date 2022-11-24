from rest_framework import serializers
from api.models import models_all
from . import serializers_print, serializers_copy, serializers_scan


class TypeOperationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models_all.TypeOperation
        fields = ("name",) #id "id"


class ScanPriceSerializer(serializers.ModelSerializer):
    operation = TypeOperationSerializer(source = 'type_operation', read_only=True)

    class Meta:
        
        model = models_all.Prices
        fields = ("operation", "price")  #id "type_operation"     