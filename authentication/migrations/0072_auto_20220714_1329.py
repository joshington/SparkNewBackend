# Generated by Django 2.2 on 2022-07-14 10:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0071_auto_20220712_0850'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailotp',
            name='initial',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 14, 13, 29, 21, 768579)),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 14, 13, 29, 21, 768579)),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 14, 13, 29, 21, 768579)),
        ),
    ]
