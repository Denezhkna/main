from django.db import models
from . import models_print, models_all, models_copy
import uuid

# Create your models here.
class HistoryScan(models.Model):
    id_session = models.CharField(max_length=50)
    date_time = models.DateTimeField(auto_now_add=True, null=True)
    operation = models.CharField(max_length=20, default=None, null=True)
    format = models.CharField(max_length=20, default=None, null=True)
    save_type = models.CharField(max_length=20, default=None, null=True)
    price = models.FloatField(max_length=50, default=None, null=True)

class FormatScan(models.Model):
    name = models.CharField(max_length=10, default=None)

class TypeScan(models.Model):
    name = models.CharField(max_length=50, default=None)

class SaveTypeScan(models.Model):
    name = models.CharField(max_length=50, default=None)






