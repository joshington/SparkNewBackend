# Generated by Django 2.2 on 2022-07-01 07:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0010_auto_20220630_1645'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 1, 10, 36, 43, 551317)),
        ),
    ]
