# Generated by Django 2.2 on 2022-07-04 06:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0030_auto_20220704_0613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 4, 6, 21, 36, 896993)),
        ),
        migrations.AlterField(
            model_name='profits',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 4, 6, 21, 36, 898924)),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 4, 6, 21, 36, 898477), editable=False),
        ),
    ]
