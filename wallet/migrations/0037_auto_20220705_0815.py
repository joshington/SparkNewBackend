# Generated by Django 2.2 on 2022-07-05 08:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0036_auto_20220705_0809'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 8, 14, 59, 884704)),
        ),
        migrations.AlterField(
            model_name='profits',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 8, 14, 59, 886554)),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 8, 14, 59, 886100), editable=False),
        ),
    ]
