# Generated by Django 2.2 on 2022-07-02 04:01

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0013_auto_20220702_0613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 7, 2, 7, 1, 15, 532248)),
        ),
    ]
