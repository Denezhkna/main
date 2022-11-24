from django.db import models
from . import models_copy, models_print, models_scan
import uuid

# Create your models here.
class TypeOperation(models.Model):
    name = models.CharField(max_length=20, default=None)

class Prices(models.Model):
    type_operation = models.OneToOneField(TypeOperation, on_delete=models.CASCADE, primary_key=False, default=0.00, related_name='type_operation')
    price = models.FloatField(max_length=50, default=None)







