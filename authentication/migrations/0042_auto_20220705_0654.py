# Generated by Django 2.2 on 2022-07-05 06:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0041_auto_20220704_0624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 6, 54, 12, 278333)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 6, 54, 12, 278352)),
        ),
    ]