# Generated by Django 2.2 on 2022-07-05 09:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0044_auto_20220705_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 9, 37, 29, 669653)),
        ),
        migrations.AlterField(
            model_name='profits',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 9, 37, 29, 672626)),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 5, 9, 37, 29, 671912), editable=False),
        ),
    ]
