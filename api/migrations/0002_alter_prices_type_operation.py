# Generated by Django 4.1.3 on 2022-11-17 08:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prices',
            name='type_operation',
            field=models.OneToOneField(default=0.0, on_delete=django.db.models.deletion.CASCADE, related_name='type_operation', to='api.typeoperation'),
        ),
    ]
