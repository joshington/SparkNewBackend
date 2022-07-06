# Generated by Django 2.2 on 2022-07-04 06:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0031_auto_20220704_0621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 4, 6, 24, 40, 154451)),
        ),
        migrations.AlterField(
            model_name='profits',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 4, 6, 24, 40, 156346)),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 4, 6, 24, 40, 155847), editable=False),
        ),
    ]
