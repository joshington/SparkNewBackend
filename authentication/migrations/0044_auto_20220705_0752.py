# Generated by Django 2.2 on 2022-07-05 07:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0043_auto_20220705_0734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 7, 51, 59, 473739)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 7, 51, 59, 473762)),
        ),
    ]