# Generated by Django 2.2 on 2022-06-30 11:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0006_auto_20220630_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='paid_at',
            field=models.DateTimeField(default=datetime.datetime(2022, 6, 30, 14, 30, 55, 918150)),
        ),
    ]
