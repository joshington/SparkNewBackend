# Generated by Django 2.2 on 2022-07-11 01:03

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0065_auto_20220709_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 11, 4, 3, 3, 718973)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 11, 4, 3, 3, 718973)),
        ),
    ]
