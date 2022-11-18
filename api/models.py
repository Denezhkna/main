from django.db import models
import uuid

# Create your models here.
class Session(models.Model):
    id_session = models.CharField(max_length=50)
    date_time = models.DateTimeField(auto_now_add=True, null=True)
    operation = models.CharField(max_length=20, default=None, null=True)
    format = models.CharField(max_length=20, default=None, null=True)
    save_type = models.CharField(max_length=20, default=None, null=True)

    
class TypeOperation(models.Model):
    name = models.CharField(max_length=20, default=None)

class Prices(models.Model):
    type_operation = models.OneToOneField(TypeOperation, on_delete=models.CASCADE, primary_key=False, default=0.00, related_name='type_operation')
    price = models.FloatField(max_length=50, default=None)

class ScanFormat(models.Model):
    name = models.CharField(max_length=10, default=None)

class ScanType(models.Model):
    name = models.CharField(max_length=50, default=None)

class ScanSaveType(models.Model):
    name = models.CharField(max_length=50, default=None)






